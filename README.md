
# ASAM ODS Jaquel MCP Server

![PyPI version](https://img.shields.io/pypi/v/odsbox-jaquel-mcp.svg)
![Apache 2.0 License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![Status](https://img.shields.io/badge/status-experimental-orange)
![Build Status](https://img.shields.io/github/actions/workflow/status/totonga/odsbox-jaquel-mcp/build.yml?branch=main)
![Stars](https://img.shields.io/github/stars/totonga/odsbox-jaquel-mcp?style=social)

<!-- mcp-name: io.github.totonga/odsbox-jaquel-mcp -->

**A Model Context Protocol (MCP) server for ASAM ODS with odsbox Jaquel query tools, ODS connection management, and measurement data access.**

---

## Overview

- 🔌 Built-in ODS connection management
- 🧰 MCP tools: schema inspection, query validation, direct ODS query execution and measurement data analysis
- 🏗️ Entity hierarchy visualization (AoTest → AoMeasurement)
- 🚀 Validate, explain and execute JAQueL queries for ASAM ODS
- 📦 Bulk timeseries/submatrix data access and script generation
- 📊 Automatic Jupyter notebook generation for measurement comparison
- 📈 Matplotlib visualization code generation
- 📉 Statistical measurement comparison and correlation analysis
- 🔎 Measurement hierarchy exploration and discovery
- 💡 Interactive starting prompts for guided workflows
- 🤖 AI-guided bulk API learning with `help_bulk_api` tool
- 📝 Comprehensive documentation and test suite

---

## Documentation

- **Prompts Guide:** See [`PROMPTS.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md) for starting prompts documentation
- **Tool Reference:** See [`TOOLS_GUIDE.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/TOOLS_GUIDE.md)
- **Changelog:** See [`CHANGELOG.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/CHANGELOG.md)

## Quick Start

### Installation

#### Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`:

```bash
uvx odsbox-jaquel-mcp@latest
```

This automatically installs and runs the server without managing virtual environments.

#### Using pipx

For a persistent installation:

```bash
pipx install odsbox-jaquel-mcp
odsbox-jaquel-mcp
```

#### Traditional pip Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install odsbox-jaquel-mcp[play]
```

> **Note:** The `[play]` extra includes optional data analysis and visualization dependencies (pandas, matplotlib, scipy) for working with Jupyter notebooks and data analysis.

### Running the Server

The server runs on stdin/stdout and waits for MCP messages from an MCP client:

```bash
# With uvx (auto-installs and runs)
uvx odsbox-jaquel-mcp@latest

# With pipx (if installed)
odsbox-jaquel-mcp

# With pip in virtual environment
python -m odsbox_jaquel_mcp
```

### Configuration for MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "ods-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["odsbox-jaquel-mcp@latest"]
    }
  }
}
```

Or with pipx:

```json
{
  "mcpServers": {
    "ods-mcp": {
      "type": "stdio",
      "command": "odsbox-jaquel-mcp"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ODSBOX_STATS_ENABLED` | not set (disabled) | Set to `1`, `true`, or `yes` to enable tool and resource call monitoring. Statistics are persisted to a SQLite database (`odsbox-jaquel-mcp-stats.db`) for cross-session tracking. |
| `FASTMCP_LOG_LEVEL` | `INFO` | Controls the server-side log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). With stdio transport all logs go to stderr, which MCP clients may display as warnings. Set to `WARNING` to reduce noise. |
| `ODSBOX_MCP_MODE` | `basic` | Authentication mode for `ods_connect_using_env`: `basic`, `m2m`, or `oidc` |
| `ODSBOX_MCP_URL` | not set | ODS server URL for `ods_connect_using_env` |
| `ODSBOX_MCP_USER` | not set | ODS username (basic mode) |
| `ODSBOX_MCP_PASSWORD` | not set | ODS password (basic mode; falls back to keyring) |
| `ODSBOX_MCP_M2M_TOKEN_ENDPOINT` | not set | OAuth2 token endpoint (m2m mode) |
| `ODSBOX_MCP_M2M_CLIENT_ID` | not set | Client ID (m2m mode) |
| `ODSBOX_MCP_M2M_CLIENT_SECRET` | not set | Client secret (m2m mode; falls back to keyring) |
| `ODSBOX_MCP_OIDC_CLIENT_ID` | not set | Client ID (oidc mode) |
| `ODSBOX_MCP_OIDC_REDIRECT_URI` | not set | Redirect URI (oidc mode, e.g. `http://127.0.0.1:1234`) |
| `ODSBOX_MCP_VERIFY` | `true` | TLS certificate verification (`true`/`false`) |

See [TOOLS_GUIDE.md](TOOLS_GUIDE.md#ods_connect_using_env) for the full list of authentication variables and keyring fallback details.

### Usage Monitoring

When `ODSBOX_STATS_ENABLED=true` is set, the server records tool call and resource read statistics to a local SQLite database:

- **Location**: `~/.local/share/odsbox-jaquel-mcp/odsbox-jaquel-mcp-stats.db` (Linux/macOS) or `%APPDATA%\odsbox-jaquel-mcp\odsbox-jaquel-mcp-stats.db` (Windows), with fallback to the system temp directory.
- **Tracked per tool**: call count, error count, total execution time (ms), last called timestamp.
- **Tracked per resource**: read count, error count, total execution time (ms), last read timestamp.
- **Cross-process safe**: uses SQLite WAL mode, so multiple concurrent MCP sessions can write safely.

You can query the stats database directly:

```bash
sqlite3 ~/.local/share/odsbox-jaquel-mcp/odsbox-jaquel-mcp-stats.db \
  "SELECT name, calls, errors, total_ms FROM tool_stats ORDER BY calls DESC"
```

Example MCP client configuration with monitoring enabled:

```json
{
  "mcpServers": {
    "ods-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["odsbox-jaquel-mcp@latest"],
      "env": {
        "ODSBOX_STATS_ENABLED": "true",
        "FASTMCP_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

## Development

### Setup

```bash
git clone https://github.com/totonga/odsbox-jaquel-mcp.git
cd odsbox-jaquel-mcp
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Common Tasks

```bash
# Run server locally
python -m odsbox_jaquel_mcp

# Run tests
pytest tests/
# or
python run_tests.py

# Code formatting and linting
ruff check .
ruff format .

# Build package
python -m build

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uvx odsbox-jaquel-mcp@latest
```

## Contributing

Pull requests and issues are welcome! Please:
- Follow PEP8 and use type hints
- Add/maintain tests for new features
- Update documentation as needed

## License

This project is licensed under the Apache License 2.0. See [LICENSE](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/LICENSE).

## Links

- [ASAM ODS](https://www.asam.net/standards/detail/ods/)
- [MCP Protocol](https://github.com/modelcontextprotocol)
- [odsbox](https://pypi.org/project/odsbox/)


## Features

### Core MCP Tools

#### Connection Management
- **ods_connect** - Establish ODS connection
- **ods_connect_using_env** - Establish ODS connection using environment variables
- **ods_disconnect** - Close ODS connection
- **ods_get_connection_info** - Get connection status

#### Schema Inspection
- **schema_get_entity** - Get all fields for entity
- **schema_list_entities** - List all entities with relationships
- **schema_test_to_measurement_hierarchy** - Get ASAM ODS test hierarchy structure

#### Query Building & Validation
- **query_validate** - Check query syntax and structure
- **query_describe** - Get plain English explanation
- **query_execute** - Execute query on ODS server

#### Timeseries/Submatrix Data Access
- **data_get_quantities** - List measurement quantities for submatrix
- **data_read_submatrix** - Read timeseries data from submatrix
- **data_generate_fetcher_script** - Generate Python scripts for data fetching

#### Pattern & Example Library
- **query_generate_skeleton** - Generate query skeleton (basic query) for entity
- **query_get_pattern** - Get template for common patterns
- **query_list_patterns** - List available patterns
- **query_get_operator_docs** - Learn about operators


### Starting Prompts
Discover and use the server's capabilities through **interactive guided prompts**:
- **ODS Server Connection** - Set up and manage connections
- **Validate a Jaquel Query** - Learn query validation
- **Explore Query Patterns** - Find common query templates
- **Bulk Data Access** - Master the 3-step Bulk API workflow
- **Measurement Analysis** - Compare measurements and visualize data

See [`PROMPTS.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md) for complete details on all starting prompts.


## Error Handling

### Common Errors and Solutions

#### Not connected
```json
{
  "error": "Model not loaded",
  "hint": "Connect to ODS server using 'ods_connect' tool first"
}
```
Solution: Call ods_connect first

#### Invalid entity
```json
{
  "error": "Entity not found: InvalidEntity",
  "available_entities": ["AoUnit", "AoMeasurement", ...]
}
```
Solution: Use valid entity from available_entities

#### Invalid field
```json
{
  "valid": false,
  "issues": ["Field 'invalid_field' not found"],
  "suggestions": ["id", "name", "description"]
}
```
Solution: Use one of the suggested fields

#### Connection failed
```json
{
  "success": false,
  "error": "Connection refused",
  "error_type": "ConnectionError"
}
```
Solution: Check URL, server availability, firewall

## Troubleshooting

### Issue: Tools not discovered
- Ensure mcp>=0.1.0 is installed
- Check ToolsCapability is set in ServerCapabilities
- Restart MCP client

### Issue: Schema tools fail
- Ensure ODS server is accessible
- Check username/password
- Verify network connectivity
- Review server logs

### Issue: Queries timeout
- Increase request_timeout in connect
- Reduce $rowlimit
- Check ODS server performance

## Performance Tips

1. **Use specific filters** - Avoid querying all records
2. **Limit rows** - Always use `$rowlimit` appropriately
3. **Select attributes** - Only retrieve needed columns/attributes
4. **Index awareness** - Filter on indexed fields first
5. **Connection reuse** - Keep connection open when possible
6. **Cache schemas** - Schema inspection is cached

## Security Notes

- Credentials are only held in memory during connection
- Connection is cleaned up on disconnect
- No credentials stored in config files
- Use HTTPS with `verify_certificate: true` for production

## Install in VSCode

![install in VSCode](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/docs/install_in_vscode.gif){width=300px}

Try with example server configuration using all three authentication modes via different env prefixes:

```json
{
	"servers": {
		"ods": {
			"type": "stdio",
			"command": "uvx",
			"args": [
				"odsbox-jaquel-mcp@latest"
			],
			"env": {
				"ODSBOX_MCP_URL": "https://docker.peak-solution.de:10032/api",
				"ODSBOX_MCP_USER": "Demo",
				"ODSBOX_MCP_PASSWORD": "mdm",
				"ODSBOX_MCP2_MODE": "m2m",
				"ODSBOX_MCP2_URL": "https://ods.example.com/api",
				"ODSBOX_MCP2_M2M_TOKEN_ENDPOINT": "https://auth.example.com/realms/myrealm/protocol/openid-connect/token",
				"ODSBOX_MCP2_M2M_CLIENT_ID": "my-service-client",
				"ODSBOX_MCP3_MODE": "oidc",
				"ODSBOX_MCP3_URL": "https://ods.example.com/api",
				"ODSBOX_MCP3_OIDC_CLIENT_ID": "my-oidc-client",
				"ODSBOX_MCP3_OIDC_REDIRECT_URI": "http://127.0.0.1:1234"
			}
		}
	},
	"inputs": []
}
```

## Support

For issues or questions:
1. Check the error message and hints
2. Review the documentation
