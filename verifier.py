from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthSnapshot:
    ready_replicas: int
    desired_replicas: int
    error_rate: float
    p95_latency_ms: float


@dataclass(frozen=True)
class VerificationResult:
    healthy: bool
    reasons: tuple[str, ...]


class HealthVerifier:
    """Compares post-action health against an independent baseline snapshot."""

    def __init__(self, max_error_rate_increase: float = 0.01, max_latency_increase_ratio: float = 0.20) -> None:
        self.max_error_rate_increase = max_error_rate_increase
        self.max_latency_increase_ratio = max_latency_increase_ratio

    def verify(self, baseline: HealthSnapshot, after: HealthSnapshot) -> VerificationResult:
        reasons: list[str] = []

        if after.ready_replicas < after.desired_replicas:
            reasons.append(
                f"Only {after.ready_replicas}/{after.desired_replicas} desired replicas are ready."
            )

        if after.error_rate > baseline.error_rate + self.max_error_rate_increase:
            reasons.append(
                f"Error rate increased from {baseline.error_rate:.4f} to {after.error_rate:.4f}."
            )

        latency_limit = baseline.p95_latency_ms * (1 + self.max_latency_increase_ratio)
        if after.p95_latency_ms > latency_limit:
            reasons.append(
                f"p95 latency increased from {baseline.p95_latency_ms:.1f}ms to "
                f"{after.p95_latency_ms:.1f}ms beyond allowed tolerance."
            )

        return VerificationResult(healthy=not reasons, reasons=tuple(reasons))
