from __future__ import annotations

from .models import ClusterContext, Decision, ExecutionPlan, RemediationRequest
from .policy import PolicyEngine


class RemediationPlanner:
    def __init__(self, policy_engine: PolicyEngine | None = None) -> None:
        self.policy_engine = policy_engine or PolicyEngine()

    def plan(self, request: RemediationRequest, context: ClusterContext) -> ExecutionPlan:
        result = self.policy_engine.evaluate(request, context)
        if result.decision != Decision.ALLOW:
            return ExecutionPlan(
                decision=result.decision,
                risk=result.risk,
                command=None,
                reasons=result.reasons,
            )

        command = self._command_for(request)
        return ExecutionPlan(
            decision=result.decision,
            risk=result.risk,
            command=command,
            reasons=result.reasons,
            verification_checks=self._verification_for(request),
            rollback_command=self._rollback_for(request),
        )

    @staticmethod
    def _command_for(request: RemediationRequest) -> tuple[str, ...]:
        base = ("kubectl", "-n", request.namespace)
        if request.action == "rollout.restart":
            return base + ("rollout", "restart", f"{request.resource_kind.lower()}/{request.resource_name}")
        if request.action == "deployment.scale":
            replicas = str(request.parameters["desired_replicas"])
            return base + ("scale", f"deployment/{request.resource_name}", f"--replicas={replicas}")
        if request.action == "pod.delete":
            return base + ("delete", "pod", request.resource_name)
        raise ValueError(f"No executable command mapping for {request.action}")

    @staticmethod
    def _verification_for(request: RemediationRequest) -> tuple[str, ...]:
        return (
            f"resource/{request.namespace}/{request.resource_name}:ready",
            "error-rate:not-worse",
            "latency:not-worse",
        )

    @staticmethod
    def _rollback_for(request: RemediationRequest) -> tuple[str, ...] | None:
        if request.action == "deployment.scale" and "current_replicas" in request.parameters:
            return (
                "kubectl",
                "-n",
                request.namespace,
                "scale",
                f"deployment/{request.resource_name}",
                f"--replicas={request.parameters['current_replicas']}",
            )
        return None
