"""Non-invasive OpenTelemetry bridge for legacy functions: wraps a
function with a trace span without requiring any change to its
internals. This is the 'strangler fig' piece of the migration, apply
it to AI-identified high-value functions incrementally."""

import functools
from collections.abc import Callable

from opentelemetry import trace

tracer = trace.get_tracer("legacy-bridge")


def instrument_legacy_function(span_name: str, **static_attributes) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                for key, value in static_attributes.items():
                    span.set_attribute(key, value)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("legacy.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("legacy.result", "failure")
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator
