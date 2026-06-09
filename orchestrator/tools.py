"""Tool definitions for Claude's converse() API."""

TOOLS = [
    {
        "toolSpec": {
            "name": "query_registry",
            "description": (
                "Search the central API registry for endpoints matching a keyword or intent. "
                "Use this tool first to discover which APIs are available before calling them."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keyword or phrase to search for (e.g., 'inventory', 'work order', 'quality')"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "call_api",
            "description": (
                "Call a registered REST API endpoint with optional query parameters. "
                "Use the endpoint URL and parameters returned from query_registry."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Full URL of the API endpoint (e.g., http://localhost:8001/lims/workorder)"
                        },
                        "params": {
                            "type": "object",
                            "description": "Query parameters as key-value pairs (e.g., {\"id\": \"WO-1234\"})"
                        }
                    },
                    "required": ["endpoint"]
                }
            }
        }
    }
]

SYSTEM_PROMPT = (
    "You are an autonomous AI agent with access to a registry of REST APIs. "
    "When a user asks a question:\n"
    "1. Use query_registry to discover relevant APIs\n"
    "2. Use call_api to invoke the appropriate endpoints\n"
    "3. Synthesize the responses into a clear, concise answer\n\n"
    "Always use tools to gather real data before answering. "
    "Be specific — include key numbers and statuses in your response."
)
