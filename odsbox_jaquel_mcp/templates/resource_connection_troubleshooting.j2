# ODS Connection Troubleshooting

## Connection Issues

### Issue 1: Connection Refused

**Cause**: ODS server not running or wrong URL

**Solutions**:
1. Verify ODS server is running
2. Check URL format: `http://host:port/api`
3. Check network connectivity: `ping host`
4. Try `localhost` instead of `127.0.0.1` or vice versa
5. Verify port number (usually 8080 or 8443)

**Test**:
```
Connect to ODS server
Check status with ods_get_connection_info
```

### Issue 2: Authentication Failed

**Cause**: Invalid credentials

**Solutions**:
1. Verify username and password
2. Check for special characters in password (may need escaping)
3. Verify user has necessary permissions
4. Check ODS server authentication configuration

**Test**:
```
Try credentials with: ods_connect
If failed, check ODS admin logs
```

### Issue 3: SSL Certificate Verification Failed

**Cause**: Self-signed certificate or certificate chain issues

**Solutions**:
1. Set `verify=false` for development/testing only
2. For production, install proper certificates
3. Update system certificate store
4. Check server certificate expiration date

**Test**:
```
Try with verify=false
If works, issue is certificate-related
```

### Issue 4: Connection Timeout

**Cause**: Network latency or server overload

**Solutions**:
1. Check network connectivity
2. Try reconnecting: `ods_disconnect` then `ods_connect`
3. Check ODS server resource usage
4. Try connecting from closer network

**Test**:
```
ods_get_connection_info
If no response, connection is dead
```

## Query Execution Issues

### Issue: Entity Not Found

**Cause**: Wrong entity name or entity doesn't exist

**Solutions**:
1. List entities: `schema_list_entities`
2. Check exact entity name (case-sensitive)
3. Verify entity is accessible

**Test**:
```
schema_list_entities
Check if your entity is in the list
```

## Data Access Issues

### Issue: Submatrix Not Found

**Cause**: Wrong submatrix ID or measurement has no data

**Solutions**:
1. Verify submatrix ID from query results
2. Check measurement has data: `data_get_quantities submatrix_id`
3. Try different measurement

### Issue: Pattern Matching Returns Empty

**Cause**: Quantity names don't match pattern

**Solutions**:
1. List quantities: `data_get_quantities submatrix_id`
2. Check exact quantity names
3. Adjust pattern (e.g., "Temp*" vs "temp*")
4. Use case-insensitive flag in `data_read_submatrix`

## Resource Cleanup

### Always Disconnect
```
When done with operations:
ods_disconnect
```

### Check Connection State
```
Before running queries:
ods_get_connection_info
```

## Getting Help

- Use `help_bulk_api` for data access questions
- Review TOOLS_GUIDE.md for detailed tool documentation
