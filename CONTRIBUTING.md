# Contributing

1. Create a feature branch.
2. Keep remediation verbs explicit and narrowly scoped.
3. Add tests for every new allow, escalate, or deny rule.
4. Do not introduce arbitrary shell execution.
5. Run `pytest` and `ruff check .` before opening a pull request.

Changes that expand execution authority should include a threat-model update.
