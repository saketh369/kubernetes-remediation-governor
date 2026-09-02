"""Tests for the non-invasive OTel bridge decorator."""

import pytest

from legacy_observability_migration.bridge.otel_decorator import instrument_legacy_function


def test_decorator_preserves_return_value():
    @instrument_legacy_function("test-span", system="test")
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


def test_decorator_reraises_exceptions():
    @instrument_legacy_function("test-span-failure")
    def always_fails():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        always_fails()
