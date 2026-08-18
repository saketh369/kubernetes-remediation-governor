# Architecture

The governor is intentionally positioned between a recommendation source and any Kubernetes mutation path.

```text
Recommendation source
        |
        v
Request normalization
        |
        v
Deterministic policy engine
  |       |        |
ALLOW  ESCALATE   DENY
  |       |        |
  v       v        v
Planner  Human    Audit
  |
  v
Bounded executor adapter
  |
  v
Kubernetes API
  |
  v
Independent verification
  |
  +--> healthy: close action
  +--> degraded: trigger rollback/escalation
```

## Design principles

1. **Default deny**: unsupported actions are rejected.
2. **No arbitrary shell**: actions map to predefined command constructors.
3. **Bounded blast radius**: scale changes and target scope are constrained.
4. **Protected control-plane namespaces**: system namespaces are denied by policy.
5. **Human approval for high-risk state changes**: stateful restarts and rollbacks escalate.
6. **Evidence-linked changes**: release rollback requires an evidence identifier.
7. **Verification is separate from recommendation**: the system that proposes a change should not be the only system deciding whether it worked.
8. **Dry-run by default**: this repository does not mutate a real cluster out of the box.
