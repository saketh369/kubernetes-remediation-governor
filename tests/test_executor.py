from kubernetes_remediation_governor.executor import DryRunExecutor
from kubernetes_remediation_governor.models import Decision, ExecutionPlan, Risk


def test_dry_run_reports_would_execute_without_mutation():
    plan = ExecutionPlan(
        decision=Decision.ALLOW,
        risk=Risk.LOW,
        command=("kubectl", "get", "pods"),
        reasons=("test",),
    )
    result = DryRunExecutor().execute(plan)
    assert result.would_execute is True
    assert "no cluster mutation" in result.message
