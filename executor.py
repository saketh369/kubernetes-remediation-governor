from __future__ import annotations

from dataclasses import dataclass

from .models import Decision, ExecutionPlan


@dataclass(frozen=True)
class ExecutionResult:
    would_execute: bool
    command: tuple[str, ...] | None
    message: str


class DryRunExecutor:
    """Safe-by-default executor that never invokes kubectl."""

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if plan.decision != Decision.ALLOW or plan.command is None:
            return ExecutionResult(False, None, f"Execution blocked: {plan.decision.value}")
        return ExecutionResult(
            True,
            plan.command,
            "Policy permits this command, but dry-run mode performed no cluster mutation.",
        )
