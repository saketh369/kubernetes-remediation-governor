"""Command-line entry points:

    legacy-scan --path ./legacy_app --out candidates.json
    legacy-infer-schema --log-file app.log
"""

import argparse
import json

from .ai.bedrock_client import BedrockClient
from .analysis.code_scanner import scan_directory
from .analysis.instrumentation_advisor import analyze_candidate, rank_recommendations
from .config.settings import settings
from .logs.pattern_sampler import sample_log_patterns
from .logs.schema_inference import infer_log_schema


def scan_command() -> None:
    parser = argparse.ArgumentParser(description="Scan a legacy codebase for instrumentation candidates")
    parser.add_argument("--path", required=True, help="Root directory of the legacy codebase")
    parser.add_argument("--out", default="instrumentation_candidates.json")
    parser.add_argument("--min-branches", type=int, default=settings.min_branch_threshold)
    args = parser.parse_args()

    bedrock = BedrockClient(region_name=settings.aws_region, model_id=settings.bedrock_model_id)
    candidates = scan_directory(args.path, min_branches=args.min_branches)

    recommendations = [analyze_candidate(bedrock, c) for c in candidates]
    ranked = rank_recommendations(recommendations)

    with open(args.out, "w") as f:
        json.dump([r.__dict__ for r in ranked], f, indent=2)

    print(f"Analyzed {len(ranked)} functions. Top priorities written to {args.out}")


def infer_schema_command() -> None:
    parser = argparse.ArgumentParser(description="Infer a structured logging schema from legacy logs")
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--sample-size", type=int, default=settings.log_sample_size)
    args = parser.parse_args()

    bedrock = BedrockClient(region_name=settings.aws_region, model_id=settings.bedrock_model_id)
    samples = sample_log_patterns(args.log_file, sample_size=args.sample_size)
    schema = infer_log_schema(bedrock, samples)

    print(schema)


if __name__ == "__main__":
    scan_command()
