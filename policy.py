from __future__ import annotations

import re
from dataclasses import dataclass

from .models import ClusterContext, Decision, PolicyResult, RemediationRequest, Risk


@dataclass(frozen=True)
class _RuleOutcome:
    name: str
    decision: Decision
    risk: Risk
    reason: str


_DECISION_WEIGHT = {Decision.ALLOW: 0, Decision.ESCALATE: 1, Decision.DENY: 2}
_RISK_WEIGHT = {Risk.LOW: 0, Risk.MEDIUM: 1, Risk.HIGH: 2, Risk.CRITICAL: 3}
_K8S_NAME = re.compile(r"^[a-z0-9](?:[-a-z0-9.]*[a-z0-9])?$")


class PolicyEngine:
    """Deterministic policy engine for untrusted remediation recommendations."""

    supported_actions = {
        "rollout.restart",
        "deployment.scale",
        "pod.delete",
        "deployment.rollback",
    }

    action_kinds = {
        "rollout.restart": {"deployment", "statefulset", "daemonset"},
        "deployment.scale": {"deployment"},
        "pod.delete": {"pod"},
        "deployment.rollback": {"deployment"},
    }

    def evaluate(self, request: RemediationRequest, context: ClusterContext) -> PolicyResult:
        outcomes: list[_RuleOutcome] = []
        kind = request.resource_kind.lower()

        if request.action not in self.supported_actions:
            outcomes.append(
                _RuleOutcome(
                    "unsupported-action",
                    Decision.DENY,
                    Risk.CRITICAL,
                    f"Action '{request.action}' is not in the explicit allowlist.",
                )
            )
        else:
            allowed_kinds = self.action_kinds[request.action]
            if kind not in allowed_kinds:
                outcomes.append(
                    _RuleOutcome(
                        "action-resource-mismatch",
                        Decision.DENY,
                        Risk.HIGH,
                        f"Action '{request.action}' is not valid for resource kind '{request.resource_kind}'.",
                    )
                )

        if not _is_k8s_name(request.namespace) or not _is_k8s_name(request.resource_name):
            outcomes.append(
                _RuleOutcome(
                    "invalid-target-identifier",
                    Decision.DENY,
                    Risk.CRITICAL,
                    "Namespace and resource name must be valid Kubernetes-style identifiers.",
                )
            )

        if request.namespace in context.protected_namespaces:
            outcomes.append(
                _RuleOutcome(
                    "protected-namespace",
                    Decision.DENY,
                    Risk.CRITICAL,
                    f"Namespace '{request.namespace}' is protected.",
                )
            )

        if kind in {"clusterrole", "clusterrolebinding", "role", "rolebinding"}:
            outcomes.append(
                _RuleOutcome(
                    "rbac-mutation",
                    Decision.DENY,
                    Risk.CRITICAL,
                    "RBAC mutations are outside the remediation boundary.",
                )
            )

        if request.action == "deployment.scale":
            current = _as_int(request.parameters.get("current_replicas"))
            desired = _as_int(request.parameters.get("desired_replicas"))
            if current is None or desired is None or desired < 0:
                outcomes.append(
                    _RuleOutcome(
                        "invalid-scale-input",
                        Decision.DENY,
                        Risk.HIGH,
                        "Scaling requires non-negative current_replicas and desired_replicas.",
                    )
                )
            else:
                delta = abs(desired - current)
                if delta > context.max_scale_delta:
                    outcomes.append(
                        _RuleOutcome(
                            "scale-delta-limit",
                            Decision.ESCALATE,
                            Risk.HIGH,
                            f"Replica delta {delta} exceeds bounded limit {context.max_scale_delta}.",
                        )
                    )
                else:
                    outcomes.append(
                        _RuleOutcome(
                            "bounded-scale",
                            Decision.ALLOW,
                            Risk.LOW,
                            f"Replica delta {delta} is within bounded limit.",
                        )
                    )

        if request.action == "pod.delete":
            owner = str(request.parameters.get("owner_kind", "")).lower()
            if owner not in {"deployment", "replicaset"}:
                outcomes.append(
                    _RuleOutcome(
                        "unmanaged-pod-delete",
                        Decision.ESCALATE,
                        Risk.HIGH,
                        "Pod deletion is only automatically allowed for replicated stateless workloads.",
                    )
                )
            else:
                outcomes.append(
                    _RuleOutcome(
                        "replicated-pod-delete",
                        Decision.ALLOW,
                        Risk.MEDIUM,
                        "Pod is owned by a replicated stateless workload.",
                    )
                )

        if request.action == "rollout.restart":
            if kind == "statefulset" and not context.allow_stateful_restart:
                outcomes.append(
                    _RuleOutcome(
                        "stateful-restart",
                        Decision.ESCALATE,
                        Risk.HIGH,
                        "Stateful workload restart requires human approval.",
                    )
                )
            else:
                outcomes.append(
                    _RuleOutcome(
                        "bounded-restart",
                        Decision.ALLOW,
                        Risk.MEDIUM,
                        "Restart is limited to one named workload.",
                    )
                )

        if request.action == "deployment.rollback":
            revision = _as_int(request.parameters.get("revision"))
            if revision is None or revision < 0:
                outcomes.append(
                    _RuleOutcome(
                        "invalid-rollback-revision",
                        Decision.DENY,
                        Risk.HIGH,
                        "Rollback requires a non-negative revision.",
                    )
                )
            elif not request.parameters.get("evidence_id"):
                outcomes.append(
                    _RuleOutcome(
                        "rollback-evidence-required",
                        Decision.ESCALATE,
                        Risk.HIGH,
                        "Rollback requires an evidence identifier tying the action to observed degradation.",
                    )
                )
            else:
                outcomes.append(
                    _RuleOutcome(
                        "evidence-backed-rollback",
                        Decision.ESCALATE,
                        Risk.HIGH,
                        "Rollback is valid but requires explicit approval because it changes release state.",
                    )
                )

        if not outcomes:
            outcomes.append(
                _RuleOutcome(
                    "default-deny",
                    Decision.DENY,
                    Risk.CRITICAL,
                    "No policy rule authorized this request.",
                )
            )

        decision = max((o.decision for o in outcomes), key=lambda x: _DECISION_WEIGHT[x])
        risk = max((o.risk for o in outcomes), key=lambda x: _RISK_WEIGHT[x])
        return PolicyResult(
            decision=decision,
            risk=risk,
            reasons=tuple(o.reason for o in outcomes),
            matched_rules=tuple(o.name for o in outcomes),
        )


def _is_k8s_name(value: str) -> bool:
    return bool(value) and len(value) <= 253 and bool(_K8S_NAME.fullmatch(value)) and not value.startswith("-")


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
