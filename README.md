# Kubernetes Remediation Governor

**Govern automated Kubernetes remediation before it reaches production.**

Kubernetes Remediation Governor is a policy-driven control-plane reference implementation for evaluating remediation requests before they are allowed to mutate a cluster.

The core idea is simple: **treat every automated or AI-generated remediation recommendation as untrusted input.** A recommendation must pass deterministic policy checks, blast-radius limits, and risk classification before an executable plan can be produced.

> This repository is a technical reference implementation and validation artifact. It does not claim enterprise production deployment or organization-wide adoption.

## Why this exists

Monitoring systems are good at detecting problems. Automation systems are good at executing commands. Recommendation engines can propose corrective actions. The dangerous gap is the boundary between **recommendation** and **execution**.

This project focuses on that boundary.

```text
Recommendation -> Policy -> Risk -> Authorization -> Plan -> Execute -> Verify -> Rollback/Escalate
```

## What makes it different

This is not another Kubernetes operator and it does not attempt to replace existing observability, GitOps, or incident-management systems.

It provides a governance layer that:

- denies unknown remediation verbs by default
- blocks protected namespaces
- blocks RBAC mutations
- constrains replica changes with explicit blast-radius limits
- escalates stateful operations and release rollbacks
- requires evidence metadata for rollback decisions
- generates commands from fixed action mappings rather than arbitrary shell input
- separates recommendation from post-change verification
- is dry-run only by default

## Decision model

| Decision | Meaning |
|---|---|
| `ALLOW` | Policy permits construction of a bounded execution plan. |
| `ESCALATE` | Request may be valid, but human approval is required. |
| `DENY` | Request violates a hard safety boundary. |

## Supported actions in v0.1

| Action | Typical outcome |
|---|---|
| `rollout.restart` | Allowed for bounded stateless workloads, escalated for StatefulSets |
| `deployment.scale` | Allowed within configured replica delta, escalated beyond it |
| `pod.delete` | Allowed only for replicated stateless ownership, otherwise escalated |
| `deployment.rollback` | Evidence required and always escalated for approval |
| Anything else | Denied |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Evaluate a safe bounded scale request:

```bash
krg examples/safe-scale.json
```

Try a stateful restart that should escalate:

```bash
krg examples/escalate-stateful-restart.json
```

Try a protected namespace mutation that should be denied:

```bash
krg examples/deny-protected-namespace.json
```

## Example

Input:

```json
{
  "action": "deployment.scale",
  "namespace": "payments",
  "resource_kind": "Deployment",
  "resource_name": "checkout-api",
  "parameters": {
    "current_replicas": 3,
    "desired_replicas": 5
  }
}
```

Policy output includes:

```text
Decision: ALLOW
Risk: LOW
Command: kubectl -n payments scale deployment/checkout-api --replicas=5
Rollback: kubectl -n payments scale deployment/checkout-api --replicas=3
```

The included executor is deliberately dry-run only and **does not execute the command against a real cluster**. The verifier compares post-action readiness, error rate, and p95 latency against a baseline health snapshot.

## Repository layout

```text
src/kubernetes_remediation_governor/
  cli.py         # CLI entrypoint
  executor.py    # safe-by-default dry-run execution adapter
  governor.py    # orchestration facade
  models.py      # typed request/result contracts
  planner.py     # bounded command construction
  policy.py      # deterministic guardrails
  verifier.py    # independent post-action health verification

tests/           # unit tests for policy, planner, and executor
examples/        # allow, escalate, and deny scenarios
docs/            # architecture and threat model
.github/workflows/ci.yml
```

## Safety boundary

The project intentionally does **not** include a live Kubernetes executor in v0.1. A production executor would require, at minimum:

- service identity and least-privilege RBAC
- signed or strongly authenticated approvals
- immutable audit logging
- policy versioning
- idempotency and concurrency controls
- independent health verification
- rollback orchestration
- rate limits and circuit breakers
- multi-cluster tenancy controls

Keeping those concerns explicit is part of the design rather than an omission hidden behind a demo.

## Testing

```bash
pytest
ruff check .
```

CI runs on Python 3.11, 3.12, and 3.13.

## Roadmap

- policy-as-code adapter interface
- Kubernetes API executor with least-privilege RBAC
- signed approval workflow for `ESCALATE`
- OpenTelemetry traces for decision and execution lifecycle
- policy version and evidence persistence
- multi-cluster tenancy boundaries
- failure-injection validation suite

## License

MIT
