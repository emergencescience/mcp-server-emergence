"""MCP server for Emergence Science platform.

A Model Context Protocol server exposing tools for the Surprisal Protocol bounty system.
"""

import asyncio
import json
import logging
import os
import sys
from collections.abc import Sequence
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Configuration
EMERGENCE_BASE_URL = os.environ.get("EMERGENCE_BASE_URL", "https://api.emergence.science")
EMERGENCE_API_KEY = os.environ.get("EMERGENCE_API_KEY", "")

# Initialize MCP server
app = Server("mcp-server-emergence")


def _headers() -> dict[str, str]:
    """Build request headers with optional auth."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "mcp-server-emergence/0.1.0",
    }
    if EMERGENCE_API_KEY:
        headers["Authorization"] = f"Bearer {EMERGENCE_API_KEY}"
        headers["X-API-Key"] = EMERGENCE_API_KEY
    return headers


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make GET request to Emergence API."""
    url = f"{EMERGENCE_BASE_URL}{path}"
    logger.info(f"GET {url}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                url,
                params=params,
                headers=_headers(),
                timeout=30.0,
            )
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise


async def _api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Make POST request to Emergence API."""
    url = f"{EMERGENCE_BASE_URL}{path}"
    logger.info(f"POST {url}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                url,
                json=payload,
                headers=_headers(),
                timeout=30.0,
            )
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise


@app.list_tools()  # type: ignore
async def list_tools() -> list[Tool]:
    """Define available MCP tools."""
    return [
        Tool(
            name="list_bounties",
            description="List available bounties on the Emergence Science platform. Filter by status, domain, or tags to discover relevant opportunities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "completed", "expired"],
                        "description": "Filter by bounty status",
                    },
                    "domain": {
                        "type": "string",
                        "description": "Filter by scientific domain (e.g., 'biology', 'physics', 'cs')",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by specific tag or keyword",
                    },
                    "tag_any": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter bounties matching any of these tags",
                    },
                    "min_reward": {
                        "type": "number",
                        "description": "Minimum reward amount to filter by",
                    },
                    "max_reward": {
                        "type": "number",
                        "description": "Maximum reward amount to filter by",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["reward", "created_at", "deadline", "surprisal_score"],
                        "default": "created_at",
                        "description": "Sort results by field",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "maximum": 100,
                        "minimum": 1,
                        "description": "Number of results to return",
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "minimum": 0,
                        "description": "Offset for pagination",
                    },
                },
            },
        ),
        Tool(
            name="get_bounty",
            description="Get detailed information about a specific bounty by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bounty_id": {
                        "type": "string",
                        "description": "Unique identifier of the bounty",
                    },
                },
                "required": ["bounty_id"],
            },
        ),
        Tool(
            name="post_bounty",
            description="Create a new bounty on the Emergence Science platform. Surprisal Protocol bounties should define clear, verifiable tasks with measurable outcomes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short, descriptive title for the bounty",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the task, requirements, and deliverables",
                    },
                    "reward": {
                        "type": "number",
                        "description": "Reward amount in specified currency",
                        "minimum": 0,
                    },
                    "currency": {
                        "type": "string",
                        "default": "USD",
                        "enum": ["USD", "ETH", "USDC", "DAI"],
                        "description": "Currency for the reward",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorizing the bounty (e.g., 'protein-folding', 'data-analysis')",
                    },
                    "domain": {
                        "type": "string",
                        "enum": ["biology", "chemistry", "physics", "computer_science", "mathematics", "medicine", "neuroscience", "climate", "materials", "other"],
                        "description": "Scientific domain of the bounty",
                    },
                    "deadline": {
                        "type": "string",
                        "format": "date-time",
                        "description": "ISO 8601 deadline for bounty completion (e.g., '2025-12-31T23:59:59Z')",
                    },
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of requirements for completion",
                    },
                    "surprisal_threshold": {
                        "type": "number",
                        "description": "Minimum surprisal score required for verification (if applicable)",
                    },
                    "verification_method": {
                        "type": "string",
                        "enum": ["automated", "manual_peer_review", "community_vote", "oracle"],
                        "default": "manual_peer_review",
                        "description": "Method used to verify task completion",
                    },
                },
                "required": ["title", "description", "reward"],
            },
        ),
        Tool(
            name="verify_task",
            description="Submit a verification for a completed bounty task. This marks submissions as approved or rejected based on validation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bounty_id": {
                        "type": "string",
                        "description": "Unique identifier of the bounty being verified",
                    },
                    "submission_id": {
                        "type": "string",
                        "description": "Unique identifier of the submission to verify",
                    },
                    "verdict": {
                        "type": "string",
                        "enum": ["approved", "rejected", "needs_revision"],
                        "description": "Verification verdict",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Detailed notes explaining the verification decision",
                    },
                    "surprisal_score": {
                        "type": "number",
                        "description": "Optional surprisal score for the submission (-inf to inf, higher = more surprising)",
                    },
                    "evidence_links": {
                        "type": "array",
                        "items": {"type": "string", "format": "uri"},
                        "description": "Links to supporting evidence or references",
                    },
                },
                "required": ["bounty_id", "submission_id", "verdict"],
            },
        ),
        Tool(
            name="submit_task",
            description="Submit a completed task/solution for a bounty.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bounty_id": {
                        "type": "string",
                        "description": "Unique identifier of the bounty",
                    },
                    "solution": {
                        "type": "string",
                        "description": "Description of the solution or findings",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "URL or reference to evidence/repository",
                    },
                    "submitter_notes": {
                        "type": "string",
                        "description": "Additional notes from submitter",
                    },
                },
                "required": ["bounty_id", "solution"],
            },
        ),
        Tool(
            name="get_domains",
            description="Get list of available scientific domains for bounties.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()  # type: ignore
async def call_tool(
    name: str, arguments: dict[str, Any] | None = None
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool invocations from MCP clients."""
    args: dict[str, Any] = arguments if isinstance(arguments, dict) else {}

    logger.info(f"Tool called: {name} with args: {json.dumps(args, default=str)}")

    try:
        if name == "list_bounties":
            # Build query parameters from arguments
            params = {k: v for k, v in args.items() if v is not None}
            data = await _api_get("/v1/bounties", params=params)

            # Format response for readability
            bounties = data.get("bounties", data) if isinstance(data, dict) else data
            summary = {
                "count": len(bounties),
                "bounties": bounties[:args.get("limit", 20)],
            }
            return [TextContent(type="text", text=json.dumps(summary, indent=2))]

        elif name == "get_bounty":
            bounty_id = args.get("bounty_id")
            if not bounty_id:
                return [TextContent(type="text", text="Error: bounty_id is required")]
            data = await _api_get(f"/v1/bounties/{bounty_id}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        elif name == "post_bounty":
            # Validate required fields
            required = ["title", "description", "reward"]
            missing = [f for f in required if not args.get(f)]
            if missing:
                return [TextContent(type="text", text=f"Error: Missing required fields: {', '.join(missing)}")]

            payload = {k: v for k, v in args.items() if v is not None}
            data = await _api_post("/v1/bounties", payload=payload)

            response = {
                "status": "success",
                "message": "Bounty posted successfully",
                "bounty": data,
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "verify_task":
            # Validate required fields
            required = ["bounty_id", "submission_id", "verdict"]
            missing = [f for f in required if not args.get(f)]
            if missing:
                return [TextContent(type="text", text=f"Error: Missing required fields: {', '.join(missing)}")]

            payload = {
                "bounty_id": args["bounty_id"],
                "submission_id": args["submission_id"],
                "verdict": args["verdict"],
                "notes": args.get("notes", ""),
            }

            # Add optional fields
            if "surprisal_score" in args:
                payload["surprisal_score"] = args["surprisal_score"]
            if "evidence_links" in args:
                payload["evidence_links"] = args["evidence_links"]

            data = await _api_post("/v1/verify", payload=payload)

            response = {
                "status": "success",
                "message": f"Submission {args['submission_id']} marked as {args['verdict']}",
                "verification": data,
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "submit_task":
            required = ["bounty_id", "solution"]
            missing = [f for f in required if not args.get(f)]
            if missing:
                return [TextContent(type="text", text=f"Error: Missing required fields: {', '.join(missing)}")]

            payload = {k: v for k, v in args.items() if v is not None}
            data = await _api_post("/v1/submissions", payload=payload)

            response = {
                "status": "success",
                "message": "Task submitted successfully",
                "submission": data,
            }
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        elif name == "get_domains":
            data = await _api_get("/v1/domains")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_msg = f"API Error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return [TextContent(type="text", text=f"{{\"error\": \"{error_msg}\"}}")]
    except Exception as e:
        error_msg = f"Internal error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=f"{{\"error\": \"{error_msg}\"}}")]


async def main() -> None:
    """Run the MCP server using stdio transport."""
    if not EMERGENCE_API_KEY:
        logger.warning("EMERGENCE_API_KEY is not set. Some operations may fail.")
    else:
        logger.info(f"Using Emergence API at: {EMERGENCE_BASE_URL}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
