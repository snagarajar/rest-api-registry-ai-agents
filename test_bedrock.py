"""Quick test to verify AWS Bedrock connectivity before the hackathon."""

import boto3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

REGION   = os.getenv("AWS_REGION", "us-west-2")
PROFILE  = os.getenv("AWS_PROFILE")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-5-20250929-v1:0")


def test_bedrock():
    print(f"Testing Bedrock (region={REGION}, profile={PROFILE or 'default'}, model={MODEL_ID})...")
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
        client  = session.client("bedrock-runtime")
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
