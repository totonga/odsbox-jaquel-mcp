# MCP Server Integration Testing Guide

This guide explains how to test the MCP server using the provided test client and integration tests.

## Overview

The MCP server can be tested at multiple levels:

1. **Unit Tests** - Test individual tool handlers with mocks (`test_mcp_server.py`)
2. **E2E Tests** - Test server communication via real stdio protocol (`test_integration_mcp_server_e2e.py`)
3. **Integration Tests** - Test with ODS server connection (`test_integration_mcp_server.py` and `test_integration_ods_connection.py`)

## Test Client: `MCPServerTestClient`

The `mcp_test_client.py` provides a test client that communicates with the MCP server via the actual stdio protocol, enabling true end-to-end testing.

### Features

- Starts MCP server as subprocess
- Communicates via JSON-RPC over stdio
- Supports async/await patterns
- Context manager support
- Timeout handling
- Tool calling and resource listing

### Basic Usage

```python
from tests.mcp_test_client import MCPServerTestClient

async def test_example():
    # Start server
    client = MCPServerTestClient()
    await client.start()
    
    try:
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")
        
        # Call a tool
        result = await client.call_tool(
            "validate_query",
            {"query": {"TestEntity": {}}}
        )
        print(f"Result: {result}")
        
        # List resources
        resources = await client.list_resources()
        print(f"Resources: {len(resources)}")
    finally:
        await client.stop()
```

### With Context Manager

```python
async def test_with_context_manager():
    async with MCPServerTestClient() as client:
        tools = await client.list_tools()
        result = await client.call_tool("validate_query", {...})
        resources = await client.list_resources()
```

### With pytest Fixtures

```python
@pytest.fixture
async def mcp_client():
    async with MCPServerTestClient() as client:
        yield client

@pytest.mark.asyncio
async def test_something(mcp_client):
    tools = await mcp_client.list_tools()
    assert len(tools) > 0
```

## Running the Tests

### E2E MCP Server Tests (Recommended)

Tests the MCP server communication protocol without needing ODS connection:

```bash
# Run all E2E tests
pytest tests/test_integration_mcp_server_e2e.py -v

# Run specific test
pytest tests/test_integration_mcp_server_e2e.py::test_server_lists_tools -v

# Run with detailed output
pytest tests/test_integration_mcp_server_e2e.py -vv -s
```

### Integration Tests with ODS

Tests MCP server with live ODS connection:

```bash
pytest tests/test_integration_mcp_server.py -m integration -v
```

### All Tests

```bash
# Unit tests only
pytest tests/test_mcp_server.py -v

# E2E tests (no ODS required)
pytest tests/test_integration_mcp_server_e2e.py -v

# MCP server integration tests
pytest tests/test_integration_mcp_server.py -v

# ODS connection tests (requires ODS)
pytest tests/test_integration_ods_connection.py -v

# All tests
pytest tests/ -v
```

## Test Architecture

### MCPServerTestClient

Located in: `tests/mcp_test_client.py`

The client:
1. Starts the MCP server as a subprocess: `python -m odsbox_jaquel_mcp`
2. Communicates via stdio streams
3. Sends JSON-RPC 2.0 requests
4. Receives JSON-RPC responses
5. Manages lifecycle with async context manager

Methods:
- `start()` - Connect to server
- `stop()` - Disconnect from server
- `call_tool(name, arguments)` - Execute a tool
- `list_tools()` - Get available tools
- `list_resources()` - Get available resources
- Async context manager support

### Test Files

#### `test_integration_mcp_server_e2e.py` - E2E MCP Protocol Tests

**Purpose**: Test MCP protocol communication end-to-end via stdio

**Status**: ✅ All 8 tests passing

**Tests**:
- `test_server_lists_tools` - Verify tools/list endpoint
- `test_server_has_expected_tools` - Check tool availability
- `test_validate_query_tool_via_mcp` - Test tool execution
- `test_list_resources` - Verify resources/list endpoint
- `test_explain_query_tool_via_mcp` - Test query explanation
- `test_get_operator_documentation_via_mcp` - Test operator docs
- `test_server_handles_invalid_tool_gracefully` - Error handling
- `test_multiple_sequential_calls` - Connection stability

**Run**:
```bash
pytest tests/test_integration_mcp_server_e2e.py -v
```

#### `test_mcp_server.py` - Existing Unit Tests

**Purpose**: Test individual tool handlers with mocks (no subprocess)

**Tests**:
- Tool definition tests
- Handler routing tests
- Tool argument validation
- Response formatting

**Run**:
```bash
pytest tests/test_mcp_server.py -v
```

#### `test_integration_mcp_server.py` - Full Integration

**Purpose**: Test MCP server startup and tool handler routing

**Status**: ✅ 2 tests passing

**Tests**:
- `test_mcp_server_process_starts` - Server subprocess startup
- `test_mcp_tool_handler_routing` - Tool handler registration

**Run**:
```bash
pytest tests/test_integration_mcp_server.py -v
```

## Debugging

### Run test with output

```bash
pytest tests/test_integration_mcp_server_e2e.py::test_server_lists_tools -vv -s
```

### Run client directly

```bash
python tests/mcp_test_client.py
```

This will:
1. Start MCP server
2. List tools
3. Call validate_query
4. Print results

### Inspect server response

```python
import asyncio
from tests.mcp_test_client import MCPServerTestClient
import json

async def debug():
    async with MCPServerTestClient() as client:
        result = await client.call_tool("validate_query", {"query": {"Test": {}}})
        print(json.dumps(result, indent=2))

asyncio.run(debug())
```

## Troubleshooting

### Server doesn't start

```bash
# Test server can run
python -m odsbox_jaquel_mcp --help

# Check if asyncio works
python -c "import asyncio; print('OK')"
```

### Timeout on tool calls

Increase timeout:
```python
client = MCPServerTestClient(timeout=30.0)  # 30 seconds
```

### Connection refused

- Ensure server module exists: `odsbox_jaquel_mcp/__main__.py`
- Verify Python path is correct
- Check filesystem permissions

### JSON parsing errors

Tool responses might need special handling:
```python
result = await client.call_tool("validate_query", {...})

# Handle different response formats
if isinstance(result, dict):
    if "result" in result:
        data = result["result"]
    elif "content" in result:
        data = result["content"]
else:
    data = result
```

## Best Practices

1. **Use fixtures for setup/teardown**
   ```python
   @pytest.fixture
   async def mcp_client():
       async with MCPServerTestClient() as client:
           yield client
   ```

2. **Test with real queries**
   ```python
   query = {
       "AoMeasurement": {"name": "Temperature*"},
       "$attributes": {"id": 1, "name": 1}
   }
   result = await mcp_client.call_tool("validate_query", {"query": query})
   ```

3. **Separate concerns**
   - `test_mcp_server.py` - Unit tests (fast)
   - `test_mcp_server_e2e.py` - Protocol tests (medium)
   - `test_integration_mcp_server.py` - Full integration (slow, optional)

4. **Run appropriate tests in CI/CD**
   ```bash
   # Quick CI tests (no ODS required)
   pytest tests/test_mcp_server.py tests/test_integration_mcp_server_e2e.py
   
   # Full tests (with ODS server available)
   pytest tests/ -v
   ```

## API Reference

### MCPServerTestClient

```python
class MCPServerTestClient:
    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize client with optional timeout."""
    
    async def start(self) -> None:
        """Start server and connect."""
    
    async def stop(self) -> None:
        """Disconnect and stop server."""
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a tool and get result."""
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools."""
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources."""
    
    async def __aenter__(self):
        """Context manager entry."""
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
```

## Further Reading

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [pytest Documentation](https://docs.pytest.org/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
