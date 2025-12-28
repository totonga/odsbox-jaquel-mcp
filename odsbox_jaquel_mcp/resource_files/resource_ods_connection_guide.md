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

## Connection Timeout & Reconnection

- Connections may timeout after inactivity
- If tools fail with connection errors, reconnect using `ods_connect`
- Check status with `ods_get_connection_info` before operations
