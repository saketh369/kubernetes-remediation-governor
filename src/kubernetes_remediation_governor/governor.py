from __future__ import annotations

from .executor import DryRunExecutor, ExecutionResult
from .models import ClusterContext, ExecutionPlan, RemediationRequest
from .planner import RemediationPlanner


class RemediationGovernor:
    def __init__(self) -> None:
        self.planner = RemediationPlanner()
        self.executor = DryRunExecutor()

    def evaluate(self, request: RemediationRequest, context: ClusterContext) -> ExecutionPlan:
        return self.planner.plan(request, context)

    def dry_run(self, request: RemediationRequest, context: ClusterContext) -> tuple[ExecutionPlan, ExecutionResult]:
        plan = self.evaluate(request, context)
        return plan, self.executor.execute(plan)
