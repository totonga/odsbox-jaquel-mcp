
# ASAM ODS Jaquel MCP Server

![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![Status](https://img.shields.io/badge/status-experimental-orange)

**A Model Context Protocol (MCP) server for ASAM ODS with Jaquel query tools, ODS connection management, and bulk data access.**

---

## Features

- 🚀 Validate, build, and optimize Jaquel queries for ASAM ODS
- 🔌 Built-in ODS connection management (no manual model injection)
- 🧰 23+ MCP tools: schema inspection, query validation, optimization, debugging, and direct ODS query execution
- 📦 Bulk timeseries/submatrix data access and script generation
- 📝 Comprehensive examples and test suite

---

## Quick Start

### Clone

```bash
git clone https://github.com/totonga/odsbox-jaquel-mcp.git
cd odsbox-jaquel-mcp
```

### Install Requirements

```bash
python -m venv .venv
source .venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Or: pip install .
```

### Running the Server

```bash
python -m odsbox_jaquel_mcp.server
```

The server will start on stdio and await MCP protocol messages.

### Testing

See examples:
```bash
python examples/usage_examples.py
python examples/use_mcp_server.py
```

Run tests:
```bash
python run_tests.py
# or
pytest tests/
```

### Building the Package

```bash
python -m build
```

## Documentation

- **Tool Reference:** See [`TOOLS_GUIDE.md`](TOOLS_GUIDE.md)
- **API & Usage:** See [`examples/`](examples/) and docstrings
- **Development:**
  - Run: `python -m odsbox_mcp_server.server`
  - Test: `python run_tests.py` or `pytest tests/`
  - Lint: `black .` and `flake8 .`

## Contributing

Pull requests and issues are welcome! Please:
- Follow PEP8 and use type hints
- Add/maintain tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Links

- [ASAM ODS](https://www.asam.net/standards/detail/ods/)
- [MCP Protocol](https://github.com/anthropics/mcp)
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

#### Connection Management (NEW)
- **connect_ods_server** - Establish ODS connection
- **disconnect_ods_server** - Close ODS connection
- **get_ods_connection_info** - Get connection status
- **execute_ods_query** - Execute query on ODS server
- **get_submatrix_measurement_quantities** - List measurement quantities for submatrix
- **read_submatrix_data** - Read timeseries data from submatrix
- **generate_submatrix_fetcher_script** - Generate Python scripts for data fetching


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
- Use strong credentials (not default "sa"/"sa")

## License

This MCP server is provided as-is for ASAM ODS integration.

## Support

For issues or questions:
1. Check the error message and hints
2. Review the documentation and examples
