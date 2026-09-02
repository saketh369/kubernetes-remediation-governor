"""Environment-driven configuration, so the same code runs locally,
in CI, or wired into a larger migration toolchain without edits."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    aws_region: str = os.environ.get("AWS_REGION", "us-east-1")
    bedrock_model_id: str = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    min_branch_threshold: int = int(os.environ.get("MIN_BRANCH_THRESHOLD", "1"))
    log_sample_size: int = int(os.environ.get("LOG_SAMPLE_SIZE", "40"))


settings = Settings()
