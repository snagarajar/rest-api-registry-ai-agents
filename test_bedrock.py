"""Quick test to verify AWS Bedrock connectivity before the hackathon."""

import boto3
import json
import sys

REGION = "us-west-2"
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


def test_bedrock():
    print(f"Testing Bedrock connection (region={REGION}, model={MODEL_ID})...")
    try:
        client = boto3.client("bedrock-runtime", region_name=REGION)
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": "Say 'Bedrock OK' and nothing else."}]}],
            inferenceConfig={"maxTokens": 20},
        )
        text = response["output"]["message"]["content"][0]["text"]
        print(f"✅  Claude responded: {text}")
    except Exception as exc:
        print(f"❌  Bedrock test failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    test_bedrock()
