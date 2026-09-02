from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(str, Enum):
    ALLOW = "ALLOW"
    ESCALATE = "ESCALATE"
    DENY = "DENY"


class Risk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RemediationRequest:
    action: str
    namespace: str
    resource_kind: str
    resource_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    reason: str = ""


@dataclass(frozen=True)
class ClusterContext:
    environment: str = "production"
    protected_namespaces: tuple[str, ...] = ("kube-system", "kube-public", "kube-node-lease")
    max_scale_delta: int = 3
    allow_stateful_restart: bool = False


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    risk: Risk
    reasons: tuple[str, ...]
    matched_rules: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionPlan:
    decision: Decision
    risk: Risk
    command: tuple[str, ...] | None
    reasons: tuple[str, ...]
    verification_checks: tuple[str, ...] = ()
    rollback_command: tuple[str, ...] | None = None
