from kubernetes_remediation_governor.models import ClusterContext, Decision, RemediationRequest
from kubernetes_remediation_governor.policy import PolicyEngine


def req(action: str, **kwargs):
    data = {
        "action": action,
        "namespace": "payments",
        "resource_kind": "Deployment",
        "resource_name": "checkout",
        "parameters": {},
    }
    data.update(kwargs)
    return RemediationRequest(**data)


def test_unknown_action_is_denied():
    result = PolicyEngine().evaluate(req("shell.exec"), ClusterContext())
    assert result.decision == Decision.DENY
    assert "unsupported-action" in result.matched_rules


def test_protected_namespace_is_denied():
    result = PolicyEngine().evaluate(req("rollout.restart", namespace="kube-system"), ClusterContext())
    assert result.decision == Decision.DENY


def test_small_scale_change_is_allowed():
    request = req("deployment.scale", parameters={"current_replicas": 3, "desired_replicas": 5})
    result = PolicyEngine().evaluate(request, ClusterContext(max_scale_delta=3))
    assert result.decision == Decision.ALLOW


def test_large_scale_change_escalates():
    request = req("deployment.scale", parameters={"current_replicas": 2, "desired_replicas": 10})
    result = PolicyEngine().evaluate(request, ClusterContext(max_scale_delta=3))
    assert result.decision == Decision.ESCALATE


def test_stateful_restart_escalates():
    request = req("rollout.restart", resource_kind="StatefulSet")
    result = PolicyEngine().evaluate(request, ClusterContext())
    assert result.decision == Decision.ESCALATE


def test_unmanaged_pod_delete_escalates():
    request = req(
        "pod.delete",
        resource_kind="Pod",
        resource_name="checkout-abc",
        parameters={"owner_kind": "StatefulSet"},
    )
    result = PolicyEngine().evaluate(request, ClusterContext())
    assert result.decision == Decision.ESCALATE


def test_rbac_mutation_is_denied_even_if_action_is_known():
    request = req("rollout.restart", resource_kind="RoleBinding")
    result = PolicyEngine().evaluate(request, ClusterContext())
    assert result.decision == Decision.DENY


def test_rollback_requires_evidence_and_approval():
    request = req("deployment.rollback", parameters={"revision": 3})
    result = PolicyEngine().evaluate(request, ClusterContext())
    assert result.decision == Decision.ESCALATE
    assert "rollback-evidence-required" in result.matched_rules
