# Architecture Overview

## Flow

1. `analysis/code_scanner.py` walks a legacy codebase and extracts function-level
   source, filtered by a branching/complexity threshold so trivial helpers are
   skipped before any AI call is made.
2. `analysis/instrumentation_advisor.py` sends each candidate function to Bedrock
   for a structured priority/reason/span-name/attributes assessment, then ranks
   the results so the highest-value functions surface first.
3. `logs/pattern_sampler.py` normalizes and deduplicates raw legacy log lines
   (numbers and UUIDs collapsed) so schema inference sees genuinely distinct
   patterns, not near-duplicates.
4. `logs/schema_inference.py` asks Bedrock to infer a structured logging schema,
   including likely correlation ID fields, from the sampled patterns.
5. `bridge/otel_decorator.py` provides a non-invasive decorator that wraps a
   legacy function with an OpenTelemetry span, with zero changes to the
   function's internals, for rolling out instrumentation incrementally to the
   AI-identified priority functions.

## Design principle

AI accelerates discovery and drafting. It does not modify legacy code directly.
Every recommendation from `legacy-scan` is meant to be human-reviewed before the
`instrument_legacy_function` decorator is applied to a given function.
