# ODS Connection Setup Guide

## Prerequisites
- ASAM ODS server URL (e.g., http://localhost:8087/api)
- Valid username and password
- Network access to ODS server

## Step 1: Connect to ODS Server

Use the `ods_connect` tool with:
- **url**: ODS REST API endpoint (e.g., `http://localhost:8087/api`)
- **username**: Authentication username
- **password**: Authentication password
- **verify** (optional): SSL certificate verification (default: true)

### Example Connection
```
URL: http://localhost:8087/api
Username: admin
Password: ****
Verify SSL: true
```

## Step 2: Verify Connection

After connecting, use `ods_get_connection_info` to verify:
- Connection status (connected/disconnected)
- Server URL and version
- Current model information

## Step 3: Explore Server Model

Once connected, explore what's available:

1. **List all entities**: Use `schema_list_entities` to see available entity types
2. **Get hierarchy**: Use `schema_test_to_measurement_hierarchy` to understand relationships
3. **Inspect entity schema**: Use `schema_get_entity` to see fields of specific entities

## Connection State Management

- **Persistent**: Connection remains active across multiple tool calls
- **One at a time**: Only one connection can be active
- **Cleanup**: Always call `ods_disconnect` when done to free resources

## SSL Certificate Handling

- **Production**: Keep `verify=true` (default) for security
- **Development/Testing**: Set `verify=false` only for self-signed certificates
- **Trust Issues**: Update system certificates or use proper certificate infrastructure

## Connecting Without Explicit Credentials

For automated/CI environments use `ods_connect_using_env` instead of `ods_connect`.
It reads all connection parameters from environment variables so no credentials appear in the conversation.

**Default prefix**: `ODSBOX_MCP`

| Auth mode | Required variables (with prefix) |
|---|---|
| `basic` (default) | `_URL`, `_USERNAME`, `_PASSWORD`, `_VERIFY` (optional) |
| `m2m` | `_URL`, `_M2M_TOKEN_ENDPOINT`, `_M2M_CLIENT_ID`, `_M2M_CLIENT_SECRET`, `_M2M_SCOPE` (optional) |
| `oidc` | `_URL`, `_OIDC_CLIENT_ID`, `_OIDC_REDIRECT_URI`, `_OIDC_AUTHORIZATION_ENDPOINT`, `_OIDC_TOKEN_ENDPOINT` |

Set the mode via `ODSBOX_MCP_MODE`. Override the prefix via `ODSBOX_MCP_ENV_PREFIX` or the `env_prefix` parameter.

## Connection Timeout & Reconnection

- Connections may timeout after inactivity
- If tools fail with connection errors, reconnect using `ods_connect` or `ods_connect_using_env`
- Check status with `ods_get_connection_info` before operations
