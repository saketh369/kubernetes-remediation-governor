"""Samples structurally distinct lines from unstructured legacy logs,
normalizing numbers and UUIDs first so near-duplicate lines don't
dominate the sample and waste schema-inference budget."""

import re
from pathlib import Path

_NUMBER_RE = re.compile(r"\d+")
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)


def _normalize(line: str) -> str:
    normalized = _UUID_RE.sub("UUID", line)
    normalized = _NUMBER_RE.sub("N", normalized)
    return normalized


def sample_log_patterns(log_file_path: str, sample_size: int = 40) -> list[str]:
    seen_patterns: set[str] = set()
    samples: list[str] = []

    with open(log_file_path, errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            normalized = _normalize(line)
            if normalized in seen_patterns:
                continue
            seen_patterns.add(normalized)
            samples.append(line)
            if len(samples) >= sample_size:
                break

    return samples
