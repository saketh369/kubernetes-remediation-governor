"""Tests for the ranking logic, using a stubbed Bedrock client."""

from legacy_observability_migration.analysis.code_scanner import FunctionCandidate
from legacy_observability_migration.analysis.instrumentation_advisor import analyze_candidate, rank_recommendations


class StubBedrockClient:
    def invoke(self, prompt: str, max_tokens: int = 250) -> str:
        return (
            "PRIORITY: high\n"
            "REASON: external I/O and error handling\n"
            "SUGGESTED_SPAN_NAME: process-order\n"
            "SUGGESTED_ATTRIBUTES: order.id, order.status"
        )


def test_analyze_candidate_parses_structured_response():
    candidate = FunctionCandidate(name="process_order", file="orders.py", source="def process_order(): pass", line_count=1)
    rec = analyze_candidate(StubBedrockClient(), candidate)

    assert rec.priority == "high"
    assert rec.suggested_span_name == "process-order"
    assert "order.id" in rec.suggested_attributes


def test_rank_recommendations_orders_by_priority():
    from legacy_observability_migration.analysis.instrumentation_advisor import InstrumentationRecommendation

    recs = [
        InstrumentationRecommendation("low_fn", "f.py", "low", "", "low-fn", []),
        InstrumentationRecommendation("high_fn", "f.py", "high", "", "high-fn", []),
        InstrumentationRecommendation("medium_fn", "f.py", "medium", "", "medium-fn", []),
    ]
    ranked = rank_recommendations(recs)
    assert [r.function_name for r in ranked] == ["high_fn", "medium_fn", "low_fn"]
