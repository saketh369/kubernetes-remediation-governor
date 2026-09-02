from kubernetes_remediation_governor.models import ClusterContext, Decision, RemediationRequest
from kubernetes_remediation_governor.planner import RemediationPlanner


def test_allowed_scale_generates_bounded_command_and_rollback():
    request = RemediationRequest(
        action="deployment.scale",
        namespace="payments",
        resource_kind="Deployment",
        resource_name="checkout",
        parameters={"current_replicas": 3, "desired_replicas": 5},
    )
    plan = RemediationPlanner().plan(request, ClusterContext(max_scale_delta=3))

    assert plan.decision == Decision.ALLOW
    assert plan.command == (
        "kubectl",
        "-n",
        "payments",
        "scale",
        "deployment/checkout",
        "--replicas=5",
    )
    assert plan.rollback_command[-1] == "--replicas=3"


def test_escalated_request_has_no_command():
    request = RemediationRequest(
        action="deployment.scale",
        namespace="payments",
        resource_kind="Deployment",
        resource_name="checkout",
        parameters={"current_replicas": 1, "desired_replicas": 10},
    )
    plan = RemediationPlanner().plan(request, ClusterContext(max_scale_delta=2))
    assert plan.decision == Decision.ESCALATE
    assert plan.command is None
