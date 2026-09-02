# Legacy Observability Migration

AI-assisted discovery and non-invasive instrumentation for migrating legacy
codebases to modern observability, without a rewrite.

Companion tooling for the article *"Migrating Legacy Systems to Modern
Observability: Using AI to Accelerate Instrumentation."*

## What it does

1. Scans a legacy codebase and ranks functions by instrumentation priority using Bedrock
2. Infers a structured logging schema from unstructured legacy log samples
3. Applies OpenTelemetry tracing to reviewed, high-priority functions via a non-invasive decorator, no changes to legacy internals required

## Project structure

```
legacy-observability-migration/
├── src/legacy_observability_migration/
│   ├── analysis/
│   │   ├── code_scanner.py          # AST-based scan, filtered by branch/complexity
│   │   └── instrumentation_advisor.py  # Bedrock review -> ranked recommendations
│   ├── logs/
│   │   ├── pattern_sampler.py       # normalize + dedupe legacy log lines
│   │   └── schema_inference.py      # Bedrock -> structured logging schema
│   ├── bridge/
│   │   └── otel_decorator.py        # non-invasive OTel span wrapper
│   ├── ai/bedrock_client.py         # single Bedrock wrapper
│   ├── config/settings.py           # env-var driven config
│   └── cli.py                       # legacy-scan / legacy-infer-schema
├── tests/                           # pytest, no AWS/Bedrock calls required
├── examples/                        # sample legacy module + log file to try the tools on
├── docs/{overview.md, usage.md}
├── scripts/bootstrap_local.sh
├── .github/workflows/ci.yml         # lint + test on push/PR
├── pyproject.toml, requirements*.txt, .env.example
└── LICENSE
```

## Quick start

```bash
git clone <your-repo-url>
cd legacy-observability-migration
bash scripts/bootstrap_local.sh
source .venv/bin/activate
cp .env.example .env   # fill in your values

# Try it on the bundled example
legacy-scan --path examples/ --out example_candidates.json
legacy-infer-schema --log-file examples/legacy_app.log
```

See [docs/usage.md](docs/usage.md) for full usage and
[docs/overview.md](docs/overview.md) for the design principles.

## Requirements

- Python 3.11+
- AWS credentials with `bedrock:InvokeModel`

## Testing

```bash
pytest --cov=legacy_observability_migration
```

All tests run without AWS credentials, no real Bedrock calls.

## License

MIT, see [LICENSE](LICENSE).
