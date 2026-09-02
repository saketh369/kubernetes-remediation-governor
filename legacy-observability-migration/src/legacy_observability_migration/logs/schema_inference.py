"""Infers a structured logging schema from sampled unstructured legacy
log lines, including which field looks like a correlation ID."""

from ..ai.bedrock_client import BedrockClient


def infer_log_schema(bedrock: BedrockClient, log_samples: list[str]) -> str:
    joined_samples = "\n".join(log_samples[:40])

    prompt = f"""These are sample lines from a legacy application's unstructured logs.

{joined_samples}

Infer a structured logging schema that would capture the same information.
List: field names, likely data types, and which fields look like they could
serve as a correlation ID (request ID, session ID, transaction ID, etc.)."""

    return bedrock.invoke(prompt, max_tokens=400)
