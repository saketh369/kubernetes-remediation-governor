"""Asks Bedrock to assess each scanned function as an instrumentation
candidate, returning a structured, ranked recommendation rather than
freeform commentary."""

import re
from dataclasses import dataclass

from ..ai.bedrock_client import BedrockClient
from .code_scanner import FunctionCandidate

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class InstrumentationRecommendation:
    function_name: str
    file: str
    priority: str
    reason: str
    suggested_span_name: str
    suggested_attributes: list[str]


def _parse_response(raw: str) -> dict:
    fields = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip().upper()] = value.strip()
    return fields


def analyze_candidate(bedrock: BedrockClient, candidate: FunctionCandidate) -> InstrumentationRecommendation:
    prompt = f"""Review this legacy function and assess it as a candidate for
OpenTelemetry instrumentation (tracing spans, key attributes, structured logging).

Function name: {candidate.name}
File: {candidate.file}
Source:
{candidate.source[:3000]}

Respond in this exact format, one field per line, no other text:
PRIORITY: [high/medium/low]
REASON: [one sentence on why, e.g. external I/O, error handling, business critical path]
SUGGESTED_SPAN_NAME: [a short, descriptive span name]
SUGGESTED_ATTRIBUTES: [comma-separated list of 2-4 attributes worth capturing]"""

    raw = bedrock.invoke(prompt, max_tokens=250)
    fields = _parse_response(raw)

    attributes = [a.strip() for a in fields.get("SUGGESTED_ATTRIBUTES", "").split(",") if a.strip()]

    return InstrumentationRecommendation(
        function_name=candidate.name,
        file=candidate.file,
        priority=fields.get("PRIORITY", "low").lower(),
        reason=fields.get("REASON", ""),
        suggested_span_name=fields.get("SUGGESTED_SPAN_NAME", re.sub(r"\W+", "-", candidate.name).lower()),
        suggested_attributes=attributes,
    )


def rank_recommendations(recs: list[InstrumentationRecommendation]) -> list[InstrumentationRecommendation]:
    return sorted(recs, key=lambda r: PRIORITY_RANK.get(r.priority, 3))
