from kubernetes_remediation_governor.executor import DryRunExecutor
from kubernetes_remediation_governor.models import Decision, ExecutionPlan, Risk


def test_dry_run_never_mutates_cluster():
    plan = ExecutionPlan(
        decision=Decision.ALLOW,
        risk=Risk.LOW,
        command=("kubectl", "get", "pods"),
        reasons=("test",),
    )
    result = DryRunExecutor().execute(plan)
    assert result.executed is True
    assert "Dry-run only" in result.message
