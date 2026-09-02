"""Single Bedrock wrapper used by both code analysis and log schema
inference, so model IDs and retry/error handling live in one place."""

import json

import boto3


class BedrockClient:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"):
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = model_id

    def invoke(self, prompt: str, max_tokens: int = 400) -> str:
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
