## Summary

Add `EmergenceBountyTools` to `langchain-community` to enable LangChain agents to interact with the [Emergence Science](https://emergence.science) bounty platform. This PR introduces three new community tools:

- `EmergenceListBounties` – Query open/completed bounties.
- `EmergencePostBounty` – Programmatically create new bounties.
- `EmergenceVerifyTask` – Verify bounty submissions and settlement.

## Motivation

Emergence Science is a growing platform for scientific research bounties. LangChain agents frequently need to discover work, fund tasks, and validate completions. A first-party community integration reduces boilerplate for users and follows patterns already established by tools like `GraphQLTool` and `OpenWeatherMapAPI`.

## Changes

- Added `langchain_community.tools.emergence` package.
- Implemented base client + three tool wrappers.
- Includes unit tests using `respx` + `pytest`.
- Added documentation strings and type hints.
- Updated `community/__init__.py` exports.

## Usage Example

```python
from langchain_community.tools.emergence import (
    EmergenceListBounties,
    EmergencePostBounty,
    EmergenceVerifyTask,
)

list_tool = EmergenceListBounties(api_key="...")
post_tool = EmergencePostBounty(api_key="...")

list_tool.invoke({"status": "open", "limit": 5})
post_tool.invoke({
    "title": "Replicate XYZ experiment",
    "description": "...",
    "reward": 500.0,
})
```

## Dependencies

- `httpx` (already an optional dep in community)
- `pydantic>=2.0`

## Testing

```bash
cd libs/community
pytest tests/unit_tests/tools/test_emergence.py -v
```

## Checklist

- [x] Added unit tests with mocked HTTP responses.
- [x] Added docstrings and type hints.
- [x] Verified `ruff` and `mypy` pass.
- [x] Updated exports in `__init__.py`.
- [ ] ( awaiting reviewer ) Integration test with live API key in CI secrets.

## Related

- Issue: emergencescience/emergence-meta#12
- MCP Server: [mcp-server-emergence](https://github.com/emergencescience/mcp-server-emergence)
