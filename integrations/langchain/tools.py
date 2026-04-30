"""LangChain Community tools for Emergence Science.

This module provides LangChain tool wrappers for the Emergence Science bounty
platform, matching the MCP server tools: list_bounties, post_bounty, verify_task.
"""

import os
from typing import Any, Optional, Type

import httpx
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

DEFAULT_BASE_URL = "https://api.emergence.science"


class _EmergenceClientMixin:
    """Lightweight async HTTP client mixin for Emergence Science API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("EMERGENCE_API_KEY", "")
        self.base_url = (base_url or os.environ.get("EMERGENCE_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.request(method, url, headers=self._headers(), **kwargs)
            resp.raise_for_status()
            return resp.json()


class EmergenceListBountiesInput(BaseModel):
    status: Optional[str] = Field(default=None, description="Filter by status: open, in_progress, completed")
    tag: Optional[str] = Field(default=None, description="Filter by tag")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class EmergenceListBounties(BaseTool, _EmergenceClientMixin):
    """Tool to list available bounties on Emergence Science."""

    name: str = "emergence_list_bounties"
    description: str = "List available bounties on Emergence Science with optional filters."
    args_schema: Type[BaseModel] = EmergenceListBountiesInput

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        BaseTool.__init__(self, **kwargs)
        _EmergenceClientMixin.__init__(self, api_key=api_key, base_url=base_url)

    def _run(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        params = {k: v for k, v in {"status": status, "tag": tag, "limit": limit, "offset": offset}.items() if v is not None}
        result = self._request("GET", "/v1/bounties", params=params)
        return str(result)


class EmergencePostBountyInput(BaseModel):
    title: str = Field(description="Short title for the bounty")
    description: str = Field(description="Detailed description")
    reward: float = Field(description="Reward amount")
    currency: str = Field(default="USD", description="Currency code")
    tags: Optional[list[str]] = Field(default=None, description="List of tags")
    deadline: Optional[str] = Field(default=None, description="ISO 8601 deadline (optional)")


class EmergencePostBounty(BaseTool, _EmergenceClientMixin):
    """Tool to create a new bounty on Emergence Science."""

    name: str = "emergence_post_bounty"
    description: str = "Create a new bounty on the Emergence Science platform."
    args_schema: Type[BaseModel] = EmergencePostBountyInput

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        BaseTool.__init__(self, **kwargs)
        _EmergenceClientMixin.__init__(self, api_key=api_key, base_url=base_url)

    def _run(
        self,
        title: str,
        description: str,
        reward: float,
        currency: str = "USD",
        tags: Optional[list[str]] = None,
        deadline: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        payload: dict[str, Any] = {
            "title": title,
            "description": description,
            "reward": reward,
            "currency": currency,
        }
        if tags:
            payload["tags"] = tags
        if deadline:
            payload["deadline"] = deadline
        result = self._request("POST", "/v1/bounties", json=payload)
        return str(result)


class EmergenceVerifyTaskInput(BaseModel):
    bounty_id: str = Field(description="Identifier of the bounty")
    submission_id: str = Field(description="Identifier of the submission to verify")
    verdict: str = Field(description="Verdict: approved or rejected")
    notes: Optional[str] = Field(default=None, description="Optional verification notes")


class EmergenceVerifyTask(BaseTool, _EmergenceClientMixin):
    """Tool to verify a bounty task on Emergence Science."""

    name: str = "emergence_verify_task"
    description: str = "Mark a bounty task as verified or rejected."
    args_schema: Type[BaseModel] = EmergenceVerifyTaskInput

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        BaseTool.__init__(self, **kwargs)
        _EmergenceClientMixin.__init__(self, api_key=api_key, base_url=base_url)

    def _run(
        self,
        bounty_id: str,
        submission_id: str,
        verdict: str,
        notes: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        payload: dict[str, Any] = {
            "bounty_id": bounty_id,
            "submission_id": submission_id,
            "verdict": verdict,
        }
        if notes:
            payload["notes"] = notes
        result = self._request("POST", "/v1/verify", json=payload)
        return str(result)
