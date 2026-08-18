from __future__ import annotations

from dataclasses import dataclass

from .models import Decision, ExecutionPlan


@dataclass(frozen=True)
class ExecutionResult:
    executed: bool
    command: tuple[str, ...] | None
    message: str


class DryRunExecutor:
    """Safe-by-default executor.

    It never invokes kubectl. A real adapter should be implemented separately and
    protected by authentication, authorization, audit logging, and approval controls.
    """

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if plan.decision != Decision.ALLOW or plan.command is None:
            return ExecutionResult(False, None, f"Execution blocked: {plan.decision.value}")
        return ExecutionResult(True, plan.command, "Dry-run only. No cluster mutation performed.")
