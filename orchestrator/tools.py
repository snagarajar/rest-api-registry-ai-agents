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
                            "description": "Keyword or phrase to search for (e.g., 'inventory', 'lab order', 'invoice')"
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
                "Call a registered REST API endpoint using GET (read-only). "
                "Use the endpoint URL and parameters returned from query_registry. "
                "Do NOT use this for creating, updating, or deleting data — use confirm_action instead."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Full URL of the API endpoint (e.g., http://localhost:8500/lab/orders)"
                        },
                        "params": {
                            "type": "object",
                            "description": "Query parameters as key-value pairs (e.g., {\"status\": \"pending\"})"
                        }
                    },
                    "required": ["endpoint"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "confirm_action",
            "description": (
                "Request user confirmation before executing any write operation "
                "(POST, PATCH, PUT, DELETE). "
                "ALWAYS call this tool instead of directly calling write endpoints. "
                "This pauses execution and shows the user what will happen before doing it.\n\n"
                "CRITICAL: If the endpoint URL contains path parameters like {order_id}, {item_id}, "
                "{invoice_id}, etc., you MUST replace them with the actual values from the user's "
                "request BEFORE passing the endpoint. "
                "Example: if endpoint template is 'http://localhost:8500/lab/orders/{order_id}/status' "
                "and the user said 'ORD-002', pass 'http://localhost:8500/lab/orders/ORD-002/status'. "
                "Never pass a URL with literal curly braces like {order_id} in it."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Human-readable description of what action will be performed (e.g., 'Create a new lab order for 20 blood samples with WGS assay')"
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method: POST, PATCH, PUT, or DELETE"
                        },
                        "endpoint": {
                            "type": "string",
                            "description": (
                                "Full URL of the write endpoint with ALL path parameters substituted. "
                                "e.g., 'http://localhost:8500/lab/orders/ORD-002/status' (NOT with {order_id}). "
                                "Replace every {param} placeholder with the real value."
                            )
                        },
                        "body": {
                            "type": "object",
                            "description": "Request body to send (key-value pairs)"
                        }
                    },
                    "required": ["description", "method", "endpoint"]
                }
            }
        }
    }
]

SYSTEM_PROMPT = (
    "You are an autonomous AI agent with access to a registry of REST APIs for an Illumina lab system. "
    "The lab system has 4 modules: Lab Orders, Inventory, Finance/Invoices, and Products — all on port 8500.\n\n"
    "When a user asks a question:\n"
    "1. Use query_registry to discover relevant APIs (1-2 searches maximum)\n"
    "2. For READ requests: use call_api to invoke GET endpoints and return the data\n"
    "3. For WRITE requests (create, update, delete, mark paid, mark as processing, etc.): use confirm_action — "
    "DO NOT call write endpoints directly. confirm_action will ask the user to confirm.\n\n"
    "PATH PARAMETER SUBSTITUTION (CRITICAL):\n"
    "- API endpoints from the registry may contain path parameters like {order_id}, {item_id}, {invoice_id}\n"
    "- You MUST replace these placeholders with actual values from the user's request\n"
    "- Example: template 'http://localhost:8500/lab/orders/{order_id}/status' + user says 'ORD-002' → "
    "pass 'http://localhost:8500/lab/orders/ORD-002/status' as the endpoint\n"
    "- NEVER pass a URL that still contains curly braces like {order_id}\n\n"
    "OTHER RULES:\n"
    "- After calling the APIs you need, STOP using tools and provide your final answer\n"
    "- Do not search the registry more than twice\n"
    "- Do not call the same endpoint twice\n"
    "- Never use call_api for POST/PATCH/PUT/DELETE — always use confirm_action for writes\n"
    "- Be specific — include key numbers, IDs, and statuses in your response"
)
