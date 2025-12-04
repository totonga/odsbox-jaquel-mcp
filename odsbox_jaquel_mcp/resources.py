"""MCP Resources for ODS connection and workflow guidance.

This module provides reference materials about:
- Connecting to ASAM ODS servers
- Common workflows and patterns
- Entity hierarchy understanding
- Query execution best practices
- Connection troubleshooting
"""

from __future__ import annotations

from mcp.types import Resource
from pydantic import AnyUrl


class ResourceLibrary:
    """Collection of reference resources for ODS operations."""

    @staticmethod
    def get_all_resources() -> list[Resource]:
        """Return all available reference resources."""
        return [
            Resource(
                uri=AnyUrl("file:///odsbox/ods-connection-guide"),
                name="ODS Connection Setup Guide",
                description="Complete guide for connecting to ASAM ODS servers and managing connections",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/ods-workflow-reference"),
                name="Common ODS Workflows",
                description="Step-by-step workflows for typical ODS operations and data access patterns",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/ods-entity-hierarchy"),
                name="ODS Entity Hierarchy Reference",
                description="Understanding ASAM ODS entity relationships (AoTest, AoMeasurement, etc.)",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/query-execution-patterns"),
                name="Query Execution Patterns",
                description="Best practices and patterns for executing Jaquel queries against ODS servers",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/query-operators-reference"),
                name="Query Operators Reference",
                description="Complete reference of all Jaquel query operators with examples and use cases",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/connection-troubleshooting"),
                name="ODS Connection Troubleshooting",
                description="Common connection issues and solutions for working with ASAM ODS servers",
                mimeType="text/markdown",
            ),
        ]

    @staticmethod
    def get_resource_content(uri: str) -> str:
        """Get the content for a specific resource.

        Args:
            uri: Resource URI (e.g., 'file:///odsbox/ods-connection-guide')

        Returns:
            Resource content as markdown
        """
        if uri == "file:///odsbox/ods-connection-guide":
            return """# ODS Connection Setup Guide

## Prerequisites
- ASAM ODS server URL (e.g., http://localhost:8087/api)
- Valid username and password
- Network access to ODS server

## Step 1: Connect to ODS Server

Use the `connect_ods_server` tool with:
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

After connecting, use `get_ods_connection_info` to verify:
- Connection status (connected/disconnected)
- Server URL and version
- Current model information

## Step 3: Explore Server Model

Once connected, explore what's available:

1. **List all entities**: Use `list_ods_entities` to see available entity types
2. **Get hierarchy**: Use `get_test_to_measurement_hierarchy` to understand relationships
3. **Inspect entity schema**: Use `check_entity_schema` to see fields of specific entities

## Connection State Management

- **Persistent**: Connection remains active across multiple tool calls
- **One at a time**: Only one connection can be active
- **Cleanup**: Always call `disconnect_ods_server` when done to free resources

## SSL Certificate Handling

- **Production**: Keep `verify=true` (default) for security
- **Development/Testing**: Set `verify=false` only for self-signed certificates
- **Trust Issues**: Update system certificates or use proper certificate infrastructure

## Connection Timeout & Reconnection

- Connections may timeout after inactivity
- If tools fail with connection errors, reconnect using `connect_ods_server`
- Check status with `get_ods_connection_info` before operations
"""

        elif uri == "file:///odsbox/ods-workflow-reference":
            return """# Common ODS Workflows

## Workflow 1: Connect and Explore Server

**Goal**: Understand what data is available on an ODS server

1. `connect_ods_server` - Connect with credentials
2. `get_ods_connection_info` - Verify connection
3. `list_ods_entities` - See all available entity types
4. `get_test_to_measurement_hierarchy` - Understand entity relationships
5. `check_entity_schema` - Inspect fields of a specific entity

**Output**: You now understand the server's data structure

## Workflow 2: Query and Execute

**Goal**: Extract data from ODS server

1. `list_query_patterns` - See available query templates
2. `get_query_pattern` - Get specific pattern
3. `explain_jaquel_query` - Understand query syntax
4. `validate_jaquel_query` - Check query syntax
5. `validate_filter_against_schema` - Test filter with real schema (requires connection)
6. `execute_ods_query` - Run query and get results

**Output**: Query results containing measurements and metadata

## Workflow 3: Read Timeseries Data

**Goal**: Access large measurement datasets efficiently

1. `execute_ods_query` - Get measurements with submatrix IDs
2. `get_submatrix_measurement_quantities` - See available time series
3. `read_submatrix_data` - Fetch data with optional pattern matching
4. `generate_submatrix_fetcher_script` - Create reusable Python script

**Output**: Timeseries data in desired format (CSV, JSON, etc.)

## Workflow 4: Analyze and Compare

**Goal**: Compare measurements across different runs/conditions

1. `execute_ods_query` - Get measurements
2. `query_measurement_hierarchy` - Explore measurement structure
   - extract_measurements: Get all measurements
   - get_unique_quantities: See available quantities
   - get_unique_tests: See all test types
3. `compare_measurements` - Statistical analysis
4. `generate_measurement_comparison_notebook` - Create Jupyter notebook

**Output**: Analysis report with statistics and visualizations

## Workflow 5: Generate Data Access Scripts

**Goal**: Create reusable Python scripts for automation

1. `read_submatrix_data` - Test data access
2. `generate_submatrix_fetcher_script` - Generate production script
3. Choose script type:
   - `basic`: Simple data fetching
   - `advanced`: With analysis and visualization
   - `batch`: For multiple submatrices
   - `analysis`: Statistical analysis included

**Output**: Python script ready for deployment
"""

        elif uri == "file:///odsbox/ods-entity-hierarchy":
            return """# ODS Entity Hierarchy Reference

## Entity Relationships

ASAM ODS uses a hierarchical structure for organizing measurements:

```
AoTest (Test/Measurement Run)
  └─ AoSubTest (Test Group)
      └─ AoMeasurement (Individual Measurement)
          └─ AoMeasurementQuantity (Time Series Data)
```

## Common Entities

### AoTest
- **Purpose**: Represents a complete test/measurement run
- **Fields**: name, description, date, duration
- **Usage**: Filter and search for specific tests
- **Example**: "Engine_Test_2024_01_15"

### AoSubTest
- **Purpose**: Groups related measurements within a test
- **Fields**: name, type, start_time, end_time
- **Usage**: Organize measurements by phase or condition
- **Example**: "Warmup_Phase", "Load_Test"

### AoMeasurement
- **Purpose**: Individual measurement instance
- **Fields**: name, unit, datatype, measurement_quantity_ids
- **Usage**: Access individual time series data
- **Example**: "Temperature", "Pressure", "RPM"

### AoMeasurementQuantity
- **Purpose**: Actual time series data
- **Fields**: Values array, timestamps
- **Usage**: Access raw measurement data
- **Example**: [25.5, 26.1, 25.9, ...]

## Navigating the Hierarchy

### Finding Tests
```
Use execute_ods_query with:
- Entity: AoTest
- Optional filters: name
```

### Finding Measurements
```
Use get_test_to_measurement_hierarchy to understand relationships
Then navigate: AoTest -> AoSubTest -> AoMeasurement -> AoMeasurementQuantity
```

### Entity Field Names
Use `check_entity_schema` to see all available fields:
- Returns field names, types, and descriptions
- Use for building accurate filter conditions
- Validate field existence with `validate_field_exists`
"""

        elif uri == "file:///odsbox/query-execution-patterns":
            return """# Query Execution Patterns

## Pattern 1: Simple Data Fetch

**When**: You want all data of a specific type

```jaquel
{
  "MeaResult": {},
  "$options": {"$rowlimit": 1000}
}
```

**Use**: `execute_ods_query` directly
**Performance**: Good for small result sets, may be slow for thousands of records

## Pattern 2: Filtered Query

**When**: You want specific measurements matching criteria

```jaquel
{
  "Test": {
      "name": {"$like": "*Engine*"}
  },
  "$options": {"$rowlimit": 1000}
}
```

**Use**: 
1. Build filter with `build_filter_condition`
2. Validate with `validate_filter_against_schema`
3. Execute with `execute_ods_query`

## Pattern 3: Bulk Data Access (Timeseries)

**When**: You need large timeseries datasets

**Steps**:
1. First, get measurement IDs: `execute_ods_query`
2. Extract submatrix IDs from results
3. Use `read_submatrix_data` instead of fetching individual points

**Why**: Bulk API is optimized for large datasets, much faster

## Pattern 4: Complex Joins

**When**: You need related data from multiple entities

```jaquel
{
  "AoMeasurement": {
    "test.name":  {"$like": "Profile*"}
  },
  "$attributes": {
    "name": 1,
    "id": 1,
    "measurement_begin": 1,
    "test.name": 1,
    "test.id": 1
  }
}
```

**Use**: 
1. Validate structure: `validate_jaquel_query`
2. Optimize: `suggest_optimizations`
3. Execute: `execute_ods_query`

## Pattern 5: Time Range Query

**When**: You want measurements from specific time window

```jaquel
{
  "AoMeasurement": {
      "measurement_begin": {
        "$gte": "2024-01-01",
        "$lte": "2024-01-31"
      }
    }
  }
}
```

**Use**: `build_filter_condition` with date operators

## Performance Tips

1. **Use Filters Early**: Filter at entity level, not after fetching
2. **Prefer Bulk API**: For timeseries data, use `read_submatrix_data`
3. **Pattern Matching**: In `read_submatrix_data`, use patterns to limit columns
4. **Pagination**: For large result sets, implement server-side pagination
"""

        elif uri == "file:///odsbox/connection-troubleshooting":
            return """# ODS Connection Troubleshooting

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
Check status with get_ods_connection_info
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
Try credentials with: connect_ods_server
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
2. Try reconnecting: `disconnect_ods_server` then `connect_ods_server`
3. Check ODS server resource usage
4. Try connecting from closer network

**Test**:
```
get_ods_connection_info
If no response, connection is dead
```

## Query Execution Issues

### Issue: Entity Not Found

**Cause**: Wrong entity name or entity doesn't exist

**Solutions**:
1. List entities: `list_ods_entities`
2. Check exact entity name (case-sensitive)
3. Verify entity is accessible

**Test**:
```
list_ods_entities
Check if your entity is in the list
```

### Issue: Invalid Filter

**Cause**: Filter field doesn't exist or wrong syntax

**Solutions**:
1. Check entity schema: `check_entity_schema EntityName`
2. Validate field exists: `validate_field_exists EntityName field_name`
3. Validate filter: `validate_filter_against_schema EntityName {filter}`
4. Check operator: `get_operator_documentation operator`

**Test**:
```
validate_filter_against_schema
Check error message for details
```

## Data Access Issues

### Issue: Submatrix Not Found

**Cause**: Wrong submatrix ID or measurement has no data

**Solutions**:
1. Verify submatrix ID from query results
2. Check measurement has data: `get_submatrix_measurement_quantities submatrix_id`
3. Try different measurement

### Issue: Pattern Matching Returns Empty

**Cause**: Quantity names don't match pattern

**Solutions**:
1. List quantities: `get_submatrix_measurement_quantities submatrix_id`
2. Check exact quantity names
3. Adjust pattern (e.g., "Temp*" vs "temp*")
4. Use case-insensitive flag in `read_submatrix_data`

## Resource Cleanup

### Always Disconnect
```
When done with operations:
disconnect_ods_server
```

### Check Connection State
```
Before running queries:
get_ods_connection_info
```

## Getting Help

- Use `get_bulk_api_help` for data access questions
- Use `debug_query_steps` to analyze query structure
- Use `suggest_error_fixes` for validation errors
- Review TOOLS_GUIDE.md for detailed tool documentation
"""

        elif uri == "file:///odsbox/query-operators-reference":
            return """# Jaquel Query Operators Reference

## Operator Categories

Jaquel provides 37 operators across 4 categories for building queries: comparison, logical operations, data aggregation, and query options.

## Comparison Operators

Use comparison operators to filter data by matching conditions.

### $eq (Equal)
- **Syntax**: `{"field": {"$eq": value}}`
- **Purpose**: Match exact value
- **Example**: `{"name": {"$eq": "Engine_Test"}}`
- **Return**: Boolean (true/false)

### $neq (Not Equal)
- **Syntax**: `{"field": {"$neq": value}}`
- **Purpose**: Exclude exact value
- **Example**: `{"status": {"$neq": "deleted"}}`
- **Return**: Boolean (true/false)

### $lt (Less Than)
- **Syntax**: `{"field": {"$lt": value}}`
- **Purpose**: Match values less than threshold
- **Example**: `{"temperature": {"$lt": 100}}`
- **Return**: Boolean (true/false)

### $gt (Greater Than)
- **Syntax**: `{"field": {"$gt": value}}`
- **Purpose**: Match values greater than threshold
- **Example**: `{"pressure": {"$gt": 50}}`
- **Return**: Boolean (true/false)

### $lte (Less Than or Equal)
- **Syntax**: `{"field": {"$lte": value}}`
- **Purpose**: Match values less than or equal to threshold
- **Example**: `{"duration": {"$lte": 3600}}`
- **Return**: Boolean (true/false)

### $gte (Greater Than or Equal)
- **Syntax**: `{"field": {"$gte": value}}`
- **Purpose**: Match values greater than or equal to threshold
- **Example**: `{"date": {"$gte": "2024-01-01"}}`
- **Return**: Boolean (true/false)

### $in (In Set)
- **Syntax**: `{"field": {"$in": [value1, value2, value3]}}`
- **Purpose**: Match any value in provided list
- **Example**: `{"status": {"$in": ["active", "pending"]}}`
- **Return**: Boolean (true/false)

### $notinset (Not In Set)
- **Syntax**: `{"field": {"$notinset": [value1, value2]}}`
- **Purpose**: Exclude any value in provided list
- **Example**: `{"level": {"$notinset": [0, -1]}}`
- **Return**: Boolean (true/false)

### $like (String Contains)
- **Syntax**: `{"field": {"$like": "pattern*"}}`
- **Purpose**: Wildcard pattern matching (* matches any characters)
- **Example**: `{"name": {"$like": "Engine*"}}`
- **Notes**: Use * for wildcards, case-sensitive by default
- **Return**: Boolean (true/false)

### $notlike (String Not Contains)
- **Syntax**: `{"field": {"$notlike": "pattern*"}}`
- **Purpose**: Inverse wildcard pattern matching
- **Example**: `{"name": {"$notlike": "Test*"}}`
- **Return**: Boolean (true/false)

### $null (Is Null)
- **Syntax**: `{"field": {"$null": true}}`
- **Purpose**: Check if field is empty/null
- **Example**: `{"notes": {"$null": true}}`
- **Return**: Boolean (true/false)

### $notnull (Is Not Null)
- **Syntax**: `{"field": {"$notnull": true}}`
- **Purpose**: Check if field has a value
- **Example**: `{"description": {"$notnull": true}}`
- **Return**: Boolean (true/false)

### $between (Range Check)
- **Syntax**: `{"field": {"$between": [min, max]}}`
- **Purpose**: Match values within inclusive range
- **Example**: `{"temperature": {"$between": [20, 30]}}`
- **Notes**: Inclusive on both ends
- **Return**: Boolean (true/false)

## Logical Operators

Use logical operators to combine multiple filter conditions.

### $and (Logical AND)
- **Syntax**: `{"$and": [condition1, condition2, ...]}`
- **Purpose**: All conditions must be true
- **Example**: `{"$and": [{"status": {"$eq": "active"}}, {"priority": {"$gt": 5}}]}`
- **Default**: Conditions at same level are implicitly AND-ed

### $or (Logical OR)
- **Syntax**: `{"$or": [condition1, condition2, ...]}`
- **Purpose**: At least one condition must be true
- **Example**: `{"$or": [{"status": {"$eq": "active"}}, {"status": {"$eq": "pending"}}]}`
- **Use**: Combine alternative conditions

### $not (Logical NOT)
- **Syntax**: `{"field": {"$not": condition}}`
- **Purpose**: Negate a condition
- **Example**: `{"status": {"$not": {"$eq": "deleted"}}}`
- **Equivalent to**: `{"status": {"$neq": "deleted"}}`

## Aggregate Functions

Use aggregate functions for data summarization and statistics.

### $none
- **Purpose**: Select no aggregation (count records)
- **Usage**: In aggregate queries
- **Return**: Record count

### $count
- **Purpose**: Count total occurrences
- **Usage**: `{"measurement": {"$count": true}}`
- **Return**: Integer count

### $dcount
- **Purpose**: Count distinct values
- **Usage**: `{"measurement": {"$dcount": true}}`
- **Return**: Integer count of unique values

### $min
- **Purpose**: Minimum value
- **Usage**: `{"temperature": {"$min": true}}`
- **Return**: Numeric minimum

### $max
- **Purpose**: Maximum value
- **Usage**: `{"temperature": {"$max": true}}`
- **Return**: Numeric maximum

### $avg
- **Purpose**: Average value
- **Usage**: `{"temperature": {"$avg": true}}`
- **Return**: Numeric average

### $stddev
- **Purpose**: Standard deviation
- **Usage**: `{"temperature": {"$stddev": true}}`
- **Return**: Numeric standard deviation

### $sum
- **Purpose**: Sum of values
- **Usage**: `{"duration": {"$sum": true}}`
- **Return**: Numeric sum

### $distinct
- **Purpose**: Get distinct values
- **Usage**: `{"status": {"$distinct": true}}`
- **Return**: Array of unique values

### $point
- **Purpose**: Extract specific value/measurement point
- **Usage**: Advanced time-series operations
- **Return**: Specific data point

### $ia (Interval Aggregation)
- **Purpose**: Aggregate over time intervals
- **Usage**: For time-series data analysis
- **Return**: Aggregated data by interval

## Special Keys & Query Options

Use special keys to control query behavior and output.

### $attributes
- **Syntax**: `{"$attributes": {"field1": 1, "field2": 1}}`
- **Purpose**: Select specific fields to return (1=include, 0=exclude)
- **Example**: `{"$attributes": {"id": 1, "name": 1, "value": 1}}`
- **Note**: Reduces response size, improves performance

### $orderby
- **Syntax**: `{"$orderby": {"field": 1}}`
- **Purpose**: Sort results (1=ascending, -1=descending)
- **Example**: `{"$orderby": {"timestamp": -1}}` (newest first)
- **Return**: Results sorted by specified order

### $groupby
- **Syntax**: `{"$groupby": "field"}`
- **Purpose**: Group results by field value
- **Example**: `{"$groupby": "measurement_type"}`
- **Combine with**: Aggregate functions

### $options
- **Syntax**: `{"$options": {option1: value1, ...}}`
- **Purpose**: Set query options (rowlimit, rowskip, etc.)
- **Example**: `{"$options": {"$rowlimit": 100}}`

### $unit
- **Syntax**: `{"$unit": "unit_name"}`
- **Purpose**: Convert values to specific unit
- **Example**: `{"$unit": "Celsius"}`
- **Usage**: For measurement data with unit conversions

### $nested
- **Syntax**: `{"field": {"$nested": {nested_condition}}}`
- **Purpose**: Query nested/related object fields
- **Example**: `{"measurement": {"$nested": {"name": {"$like": "Temp*"}}}}`

### $rowlimit
- **Syntax**: `{"$options": {"$rowlimit": number}}`
- **Purpose**: Limit number of rows returned
- **Example**: `{"$options": {"$rowlimit": 1000}}`
- **Default**: Server-dependent

### $rowskip
- **Syntax**: `{"$options": {"$rowskip": number}}`
- **Purpose**: Skip first N rows (pagination)
- **Example**: `{"$options": {"$rowskip": 500, "$rowlimit": 100}}`

### $seqlimit
- **Syntax**: `{"$options": {"$seqlimit": number}}`
- **Purpose**: Limit sequence/time-series length
- **Example**: `{"$options": {"$seqlimit": 10000}}`

### $seqskip
- **Syntax**: `{"$options": {"$seqskip": number}}`
- **Purpose**: Skip first N sequence elements
- **Example**: `{"$options": {"$seqskip": 100}}`

## Common Operator Combinations

### Example 1: Filtered Query with Attributes
```jaquel
{
  "AoMeasurement": {
    "name": {"$like": "Temp*"},
    "value": {"$gte": 0}
  },
  "$attributes": {
    "id": 1,
    "name": 1,
    "value": 1
  },
  "$options": {
    "$rowlimit": 100
  }
}
```

### Example 2: Time Range with Sorting
```jaquel
{
  "AoMeasurement": {
    "timestamp": {
      "$gte": "2024-01-01",
      "$lte": "2024-01-31"
    }
  },
  "$orderby": {"timestamp": 1},
  "$options": {"$rowlimit": 500}
}
```

### Example 3: Aggregate Query
```jaquel
{
  "AoMeasurement": {
    "measurement_type": {"$in": ["pressure", "temperature"]}
  },
  "$groupby": "measurement_type",
  "value": {"$avg": true}
}
```

## Using Operators with Tools

- **build_filter_condition**: Create complex filters using comparison & logical operators
- **validate_filter_against_schema**: Verify operators are valid for entity
- **execute_ods_query**: Run query with all operators
- **get_operator_documentation**: Get detailed docs for any operator
- **suggest_optimizations**: Get performance tips for your operators

## Performance Tips

1. **Filter Early**: Apply $eq and specific operators first
2. **Use $attributes**: Only select needed fields
3. **Use $rowlimit**: Always set limit for large queries
4. **Avoid $notlike**: Use $like with patterns instead when possible
5. **Groupby with aggregates**: Combine for summary queries
"""

        else:
            return f"Unknown resource: {uri}"
