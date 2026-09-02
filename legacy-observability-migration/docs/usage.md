# Usage

## Scan a legacy codebase for instrumentation candidates

```bash
legacy-scan --path ./path/to/legacy_app --out candidates.json
```

Review `candidates.json`, ranked high to low priority. Each entry includes a
suggested span name and attributes.

## Infer a structured schema from unstructured logs

```bash
legacy-infer-schema --log-file ./path/to/app.log
```

## Apply the non-invasive bridge to a reviewed function

```python
from legacy_observability_migration.bridge.otel_decorator import instrument_legacy_function

@instrument_legacy_function("process-order-legacy", system="order-processing")
def process_order(order_id, items):
    # untouched legacy business logic
    ...
```

## Try it on the bundled example

```bash
legacy-scan --path examples/ --out example_candidates.json
legacy-infer-schema --log-file examples/legacy_app.log
```
