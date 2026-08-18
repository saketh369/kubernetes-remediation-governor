# Threat model

## Assets protected

- Kubernetes workload availability
- Namespace and RBAC boundaries
- Release state
- Cluster capacity
- Auditability of automated actions

## Primary threats

### Hallucinated or unsafe recommendation
A recommendation engine proposes an unsupported or destructive action.

**Control:** explicit action allowlist and default-deny policy.

### Prompt or input injection into execution
Untrusted text attempts to smuggle arbitrary shell arguments into a remediation.

**Control:** no shell interpolation. Commands are constructed from typed fields and fixed verbs.

### Excessive blast radius
A valid action targets a protected namespace or requests an unbounded capacity change.

**Control:** protected namespace deny rules and scale-delta limits.

### Stateful workload disruption
A restart or rollback could create data or availability risk.

**Control:** high-risk operations escalate for approval.

### False-positive success
The change executes but service health degrades.

**Control:** post-action verification contract and rollback hook in the execution plan.

## Out of scope for v0.1

- Production authentication and authorization
- Kubernetes API credentials
- Secret management
- Multi-cluster tenancy
- Signed approvals
- Persistent audit storage
- Production-grade rollback orchestration
