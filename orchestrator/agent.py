"""Claude orchestrator agent via AWS Bedrock converse() API."""

import json
import logging
import os

import boto3
import requests
from dotenv import load_dotenv

from orchestrator.tools import TOOLS, SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_PROFILE = os.getenv("AWS_PROFILE")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-5-20250929-v1:0")
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:9000")

session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
bedrock = session.client("bedrock-runtime")


# ─── Tool Implementations ─────────────────────────────────────────────────────

def query_registry(query: str) -> list:
    """Search the API registry and return matching endpoint metadata."""
    logger.info("[tool] query_registry: %s", query)
    try:
        resp = requests.get(f"{REGISTRY_URL}/registry/search", params={"query": query}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("apis", [])
    except Exception as exc:
        logger.error("query_registry failed: %s", exc)
        return [{"error": str(exc)}]


def call_api(endpoint: str, params: dict | None = None) -> dict:
    """Invoke a registered REST API endpoint."""
    logger.info("[tool] call_api: %s params=%s", endpoint, params)
    try:
        resp = requests.get(endpoint, params=params or {}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "detail": exc.response.text}
    except Exception as exc:
        logger.error("call_api failed: %s", exc)
        return {"error": str(exc)}


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch tool call and return result as JSON string."""
    if tool_name == "query_registry":
        result = query_registry(tool_input["query"])
    elif tool_name == "call_api":
        result = call_api(tool_input["endpoint"], tool_input.get("params"))
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    return json.dumps(result)


# ─── Orchestrator ─────────────────────────────────────────────────────────────

def orchestrate(user_question: str) -> str:
    """
    Run the Claude agent loop:
    - Send user question
    - Handle tool_use calls until Claude returns end_turn
    - Return Claude's final text answer
    """
    logger.info("Orchestrating: %s", user_question)

    messages = [{"role": "user", "content": [{"text": user_question}]}]

    for iteration in range(10):  # safety cap to prevent infinite loops
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=messages,
            system=[{"text": SYSTEM_PROMPT}],
            toolConfig={"tools": TOOLS},
            inferenceConfig={"maxTokens": 2048, "temperature": 0},
        )

        stop_reason = response["stopReason"]
        assistant_message = response["output"]["message"]
        messages.append(assistant_message)

        logger.info("Iteration %d — stopReason: %s", iteration + 1, stop_reason)

        if stop_reason == "end_turn":
            for block in assistant_message["content"]:
                if block.get("type") == "text":
                    return block["text"]
            return "No response generated."

        if stop_reason == "tool_use":
            tool_results = []
            for block in assistant_message["content"]:
                if block.get("type") == "toolUse":
                    tool_result_content = _execute_tool(block["name"], block["input"])
                    tool_results.append({
                        "type": "toolResult",
                        "toolUseId": block["toolUseId"],
                        "content": tool_result_content,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            logger.warning("Unexpected stopReason: %s", stop_reason)
            break

    return "Agent reached iteration limit without a final answer."
