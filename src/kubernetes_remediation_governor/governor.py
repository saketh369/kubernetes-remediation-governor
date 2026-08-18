from __future__ import annotations

from .executor import DryRunExecutor, ExecutionResult
from .models import ClusterContext, ExecutionPlan, RemediationRequest
from .planner import RemediationPlanner
from .verifier import HealthSnapshot, HealthVerifier, VerificationResult


class RemediationGovernor:
    def __init__(self) -> None:
        self.planner = RemediationPlanner()
        self.executor = DryRunExecutor()
        self.verifier = HealthVerifier()

    def evaluate(self, request: RemediationRequest, context: ClusterContext) -> ExecutionPlan:
        return self.planner.plan(request, context)

    def dry_run(
        self, request: RemediationRequest, context: ClusterContext
    ) -> tuple[ExecutionPlan, ExecutionResult]:
        plan = self.evaluate(request, context)
        return plan, self.executor.execute(plan)

    def verify(self, baseline: HealthSnapshot, after: HealthSnapshot) -> VerificationResult:
        return self.verifier.verify(baseline, after)
