# mcp-server-emergence

A minimal [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for the [Emergence Science](https://emergence.science) platform. Provides tools to list bounties, post new bounties, and verify completed tasks for the Surprisal Protocol.

## Features

- **list_bounties**: Discover available bounties with flexible filtering (status, domain, tags, reward range)
- **get_bounty**: Get detailed information about a specific bounty
- **post_bounty**: Create new scientific bounties with surprisal scoring
- **verify_task**: Verify submissions and mark them as approved/rejected
- **submit_task**: Submit completed tasks for bounties
- **get_domains**: Browse available scientific domains

## Installation

### From PyPI (when published)
```bash
pip install mcp-server-emergence
```

### From Source
```bash
git clone https://github.com/emergencescience/mcp-server-emergence.git
cd mcp-server-emergence
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMERGENCE_API_KEY` | Yes | - | Your Emergence Science API key |
| `EMERGENCE_BASE_URL` | No | `https://api.emergence.science` | Base URL for the Emergence API |

```bash
export EMERGENCE_API_KEY="your-api-key-here"
export EMERGENCE_BASE_URL="https://api.emergence.science"
```

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "emergence": {
      "command": "uvx",
      "args": ["mcp-server-emergence"],
      "env": {
        "EMERGENCE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or if using Python directly:

```json
{
  "mcpServers": {
    "emergence": {
      "command": "python",
      "args": ["-m", "mcp_server_emergence.server"],
      "env": {
        "EMERGENCE_API_KEY": "your-api-key-here",
        "EMERGENCE_BASE_URL": "https://api.emergence.science"
      }
    }
  }
}
```

## Usage

### Running Standalone

```bash
# After installing
mcp-server-emergence

# Or using Python
python -m mcp_server_emergence.server
```

### Using with Claude Desktop

Once configured, Claude Desktop will automatically start the MCP server. You can then ask Claude to:

- "List open bounties in computer science"
- "Show me bounties with rewards over $1000"
- "Post a new bounty for analyzing protein folding data"
- "Verify submission XYZ for bounty ABC"

## Available Tools

| Tool | Description |
|------|-------------|
| `list_bounties` | List available bounties with optional filters (status, domain, tags, reward range, sort) |
| `get_bounty` | Get detailed information about a specific bounty by ID |
| `post_bounty` | Create a new bounty with title, description, reward, domain, tags, and verification method |
| `verify_task` | Submit verification for a completed task (approved/rejected/needs_revision) |
| `submit_task` | Submit a completed solution for a bounty |
| `get_domains` | Retrieve list of available scientific domains |

## API Endpoints

The server connects to the Emergence Science API at:

- `GET /v1/bounties` - List bounties
- `GET /v1/bounties/{id}` - Get bounty details
- `POST /v1/bounties` - Create bounty
- `POST /v1/verify` - Verify task
- `POST /v1/submissions` - Submit task
- `GET /v1/domains` - List domains

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
ruff format src/

# Test server
python test_server.py
```

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
│    (MCP Client) │
└────────┬────────┘
         │ stdio
┌────────▼────────┐
│ MCP Server      │
│ (this package)  │
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│ Emergence API   │
│ emergence.science│
└─────────────────┘
```

## License

MIT

## Contributing

Contributions welcome! Please see the [Emergence Science](https://emergence.science) project guidelines.

## Links

- [MCP Protocol](https://modelcontextprotocol.io/)
- [Emergence Science](https://emergence.science)
- [Emergence API Docs](https://emergence.science/api)
