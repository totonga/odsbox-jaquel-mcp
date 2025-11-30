
# ASAM ODS Jaquel MCP Server

![PyPI version](https://img.shields.io/pypi/v/odsbox-jaquel-mcp.svg)
![Apache 2.0 License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![Status](https://img.shields.io/badge/status-experimental-orange)
![Build Status](https://img.shields.io/github/actions/workflow/status/totonga/odsbox-jaquel-mcp/build.yml?branch=main)
![Stars](https://img.shields.io/github/stars/totonga/odsbox-jaquel-mcp?style=social)

**A Model Context Protocol (MCP) server for ASAM ODS with odsbox Jaquel query tools, ODS connection management, and measurement data access.**

---

## Overview

- 🔌 Built-in ODS connection management
- 🧰 29+ MCP tools: schema inspection, query validation, optimization, debugging, and direct ODS query execution
- 🏗️ Entity hierarchy visualization (AoTest → AoMeasurement)
- 🚀 Validate, build, and optimize Jaquel queries for ASAM ODS
- 📦 Bulk timeseries/submatrix data access and script generation
- 📊 Automatic Jupyter notebook generation for measurement comparison
- 📈 Matplotlib visualization code generation
- 📉 Statistical measurement comparison and correlation analysis
- 🔎 Measurement hierarchy exploration and discovery
- 💡 Interactive starting prompts for guided workflows
- 🤖 AI-guided bulk API learning with `get_bulk_api_help` tool
- 📝 Comprehensive examples, documentation, and test suite

---

## Documentation

- **Prompts Guide:** See [`PROMPTS.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md) for starting prompts documentation
- **Tool Reference:** See [`TOOLS_GUIDE.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/TOOLS_GUIDE.md)

## Quick Start

### Installation

#### Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`:

```bash
uvx odsbox-jaquel-mcp
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
uvx odsbox-jaquel-mcp

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
    "odsbox-jaquel": {
      "command": "uvx",
      "args": ["odsbox-jaquel-mcp"]
    }
  }
}
```

Or with pipx:

```json
{
  "mcpServers": {
    "odsbox-jaquel": {
      "command": "odsbox-jaquel-mcp"
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
black .
isort .
flake8 .

# Build package
python -m build

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uvx odsbox-jaquel-mcp
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

### Core Validation Tools

#### Query Building & Validation
- **validate_jaquel_query** - Check query syntax and structure
- **validate_filter_condition** - Validate filter conditions
- **build_filter_condition** - Construct filter conditions
- **explain_jaquel_query** - Get plain English explanation

#### Pattern & Example Library
- **get_query_pattern** - Get template for common patterns
- **list_query_patterns** - List available patterns
- **generate_query_skeleton** - Generate query skeleton for entity
- **get_operator_documentation** - Learn about operators

#### Query Optimization
- **suggest_optimizations** - Get optimization suggestions
- **merge_filter_conditions** - Combine multiple conditions

#### Debugging Tools
- **debug_query_steps** - Break query into logical steps
- **suggest_error_fixes** - Get suggestions for errors

#### Schema Inspection (Requires Connection)
- **check_entity_schema** - Get all fields for entity
- **validate_field_exists** - Check if field exists
- **validate_filter_against_schema** - Validate against schema
- **list_ods_entities** - List all entities with relationships
- **get_test_to_measurement_hierarchy** - Get ASAM ODS test hierarchy structure

#### Connection Management (NEW)
- **connect_ods_server** - Establish ODS connection
- **disconnect_ods_server** - Close ODS connection
- **get_ods_connection_info** - Get connection status
- **execute_ods_query** - Execute query on ODS server
- **get_submatrix_measurement_quantities** - List measurement quantities for submatrix
- **read_submatrix_data** - Read timeseries data from submatrix
- **generate_submatrix_fetcher_script** - Generate Python scripts for data fetching

### Starting Prompts
Discover and use the server's capabilities through **interactive guided prompts**:
- **Validate a Jaquel Query** - Learn query validation
- **Explore Query Patterns** - Find common query templates
- **ODS Server Connection** - Set up and manage connections
- **Build Filter Conditions** - Master WHERE clause construction
- **Bulk Data Access** - Master the 3-step Bulk API workflow
- **Measurement Analysis** - Compare measurements and visualize data
- **Optimize & Debug** - Improve query performance

See [`PROMPTS.md`](https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md) for complete details on all starting prompts.


## Error Handling

### Common Errors and Solutions

#### Not connected
```json
{
  "error": "Model not loaded",
  "hint": "Connect to ODS server using 'connect_ods_server' tool first"
}
```
Solution: Call connect_ods_server first

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
- Optimize query with suggest_optimizations
- Reduce $rowlimit
- Check ODS server performance

## Performance Tips

1. **Use specific filters** - Avoid querying all records
2. **Limit rows** - Always use `$rowlimit` appropriately
3. **Select attributes** - Only retrieve needed columns
4. **Index awareness** - Filter on indexed fields first
5. **Connection reuse** - Keep connection open when possible
6. **Cache schemas** - Schema inspection is cached

## Security Notes

- Credentials are only held in memory during connection
- Connection is cleaned up on disconnect
- No credentials stored in config files
- Use HTTPS with `verify_certificate: true` for production

## Support

For issues or questions:
1. Check the error message and hints
2. Review the documentation and examples
