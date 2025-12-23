"""MCP Resources for ODS connection and workflow guidance.

This module provides reference materials about:
- Connecting to ASAM ODS servers
- Common workflows and patterns
- Entity hierarchy understanding
- Query execution best practices
- Connection troubleshooting
- Dynamic entity schema templates
"""

from __future__ import annotations

from mcp.types import Resource, ResourceTemplate
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
                uri=AnyUrl("file:///odsbox/jaquel-syntax-guide"),
                name="Jaquel Syntax Guide",
                description="Complete Jaquel query language syntax reference with examples and best practices",
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
    def get_all_resource_templates() -> list[ResourceTemplate]:
        """Return all available resource templates for dynamic content."""
        return [
            ResourceTemplate(
                name="entity_schema",
                uriTemplate="file:///odsbox/schema/entity/{entity_name}",
                title="Entity Schema",
                description="Get detailed schema information for any ODS entity (requires active ODS connection)",
                mimeType="text/markdown",
            ),
        ]

    @staticmethod
    def get_resource_content(uri: str) -> str:
        """Get the content for a specific resource.

        Args:
            uri: Resource URI (e.g., 'file:///odsbox/ods-connection-guide' or 'file:///odsbox/schema/AoTest')

        Returns:
            Resource content as markdown
        """
        # Handle dynamic entity schema template
        if uri.startswith("file:///odsbox/schema/entity/"):
            from .schemas import SchemaInspector

            entity_name = uri.replace("file:///odsbox/schema/entity/", "")
            try:
                return SchemaInspector.format_entity_schema_as_markdown(entity_name)
            except Exception as e:
                return f"""# Entity Schema: {entity_name}

**Error retrieving schema**: {str(e)}

Ensure:
1. You are connected to an ODS server via `connect_ods_server` tool
2. The entity name is correct (try `list_ods_entities` to see available entities)
3. The entity exists in the ODS model
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

## Performance Tips

1. **Filter Early**: Apply $eq and specific operators first
2. **Use $attributes**: Only select needed fields
3. **Use $rowlimit**: Always set limit for large queries
4. **Avoid $notlike**: Use $like with patterns instead when possible
5. **Groupby with aggregates**: Combine for summary queries
"""

        elif uri == "file:///odsbox/jaquel-syntax-guide":
            return """# Jaquel Syntax Guide

Jaquel (JAQ query language for Elements) is the query language used to query ASAM ODS servers. This guide covers the complete syntax with practical examples.

## Important Note on Names

It is always possible to use **application or base names** for entity, relations, and attributes. The lookup order is:

1. Application name
2. Base name

If a base name is not uniquely assigned in the model, just one is picked. This allows you to write generic code without analyzing the complete application model. Application names can always be used to access any element or attribute.

## Basic Query Structure

All queries are JSON objects that follow this general pattern:

```jaquel
{
    "EntityName": {
        // Filter conditions (optional)
    },
    "$attributes": {
        // Fields to retrieve (optional)
    },
    "$options": {
        // Query options (optional)
    }
}
```

## Query Examples

### Get All Instances

Get all AoTest instances:

```python
r = con_i.query({
    "AoTest": {}
})
```

### Access by ID

Get a measurement with ID 4711:

```python
# Using ID directly
r = con_i.query({
    "AoMeasurement": 4711
})

# ID as string
r = con_i.query({
    "AoMeasurement": "4711"
})

# ID as explicit condition
r = con_i.query({
    "AoMeasurement": {
        "id": 4711
    }
})

# Using application names
r = con_i.query({
    "MeaResult": {
        "Id": 4711
    }
})
```

### Get Children

Get all measurements of a given SubTest:

```python
# Using parent ID
r = con_i.query({
    "AoMeasurement": {
        "test": 4611
    }
})

# Using parent ID explicitly
r = con_i.query({
    "AoMeasurement": {
        "test.id": 4611
    }
})

# Using inverse relationship
r = con_i.query({
    "AoSubTest": "4611",
    "$attributes": {
        "children.name": 1,
        "children.id": 1
    }
})

# Or with nested attributes
r = con_i.query({
    "AoSubTest": "4611",
    "$attributes": {
        "children": {
            "name": 1,
            "id": 1
        }
    }
})
```

### Search by Multiple Conditions

Search for a TestSequence by name and version:

```python
r = con_i.query({
    "AoTestSequence": {
        "name": "MyTestSequence",
        "version": "V1"
    }
})
```

### Case-Insensitive Matching

```python
# Case insensitive exact match
r = con_i.query({
    "AoTest": {
        "name": {
            "$eq": "MyTest",
            "$options": "i"
        }
    }
})

# Case insensitive wildcard match
r = con_i.query({
    "AoTest": {
        "name": {
            "$like": "My*",
            "$options": "i"
        }
    }
})
```

### Resolve ASAM Path

Navigate hierarchical relationships:

```python
# Flat style with dot notation
r = con_i.query({
    "AoMeasurement": {
        "name": "MyMea",
        "version": "V1",
        "test.name": "MySubTest2",
        "test.version": "V1",
        "test.parent_test.name": "MySubTest1",
        "test.parent_test.version": "V1",
        "test.parent_test.parent_test.name": "MyTest",
        "test.parent_test.parent_test.version": "V1"
    }
})

# Nested style
r = con_i.query({
    "AoMeasurement": {
        "name": "MyMea",
        "version": "V1",
        "test": {
            "name": "MySubTest2",
            "version": "V1",
            "parent_test": {
                "name": "MySubTest1",
                "version": "V1",
                "parent_test": {
                    "name": "MyTest",
                    "version": "V1"
                }
            }
        }
    }
})
```

## Comparison Operators

### $in - Contains in Array

```python
r = con_i.query({
    "AoMeasurement": {
        "id": {
            "$in": [4711, 4712, 4713]
        }
    }
})
```

### Time Range Queries

Search for a specific time span:

```python
r = con_i.query({
    "AoMeasurement": {
        "measurement_begin": {
            "$gte": "2012-04-23T00:00:00.000Z",
            "$lt": "2012-04-24T00:00:00.000Z"
        }
    }
})
```

Use $between operator:

```python
r = con_i.query({
    "AoMeasurement": {
        "measurement_begin": {
            "$between": ["2012-04-23T00:00:00.000Z", "2012-04-24T00:00:00.000Z"]
        }
    }
})
```

## Logical Operators

### $and - Logical AND

```python
r = con_i.query({
    "AoMeasurement": {
        "$and": [
            {
                "measurement_begin": {
                    "$gte": "2012-04-23T00:00:00.000Z",
                    "$lt": "2012-04-24T00:00:00.000Z"
                }
            },
            {
                "measurement_end": {
                    "$gte": "2012-04-23T00:00:00.000Z",
                    "$lt": "2012-04-24T00:00:00.000Z"
                }
            }
        ]
    }
})
```

### $or - Logical OR

```python
r = con_i.query({
    "AoMeasurement": {
        "$or": [
            {
                "measurement_begin": {
                    "$gte": "2012-04-23T00:00:00.000Z",
                    "$lt": "2012-04-24T00:00:00.000Z"
                }
            },
            {
                "measurement_begin": {
                    "$gte": "2012-05-23T00:00:00.000Z",
                    "$lt": "2012-05-24T00:00:00.000Z"
                }
            },
            {
                "measurement_begin": {
                    "$gte": "2012-06-23T00:00:00.000Z",
                    "$lt": "2012-06-24T00:00:00.000Z"
                }
            }
        ]
    }
})
```

### $not - Logical NOT

```python
r = con_i.query({
    "AoTestSequence": {
        "$not": {
            "$and": [
                {"name": "MyTestSequence"},
                {"version": "V1"}
            ]
        }
    }
})
```

### Mixed Case Sensitive/Insensitive

```python
r = con_i.query({
    "AoTest": {
        "$and": [
            {
                "name": {
                    "$like": "My*",
                    "$options": "i"
                }
            },
            {
                "name": {
                    "$like": "??Test"
                }
            }
        ]
    }
})
```

## Units and Aggregates

### Define Unit for Retrieved Attributes

```python
r = con_i.query({
    "AoMeasurementQuantity": 4711,
    "$attributes": {
        "name": 1,
        "id": 1,
        "maximum": {
            "$unit": 1234
        }
    }
})
```

### Define Unit for Condition Values

```python
r = con_i.query({
    "AoMeasurementQuantity": {
        "maximum": {
            "$unit": 3,
            "$between": [1.2, 2.3]
        }
    }
})
```

### Access Min and Max Values

```python
r = con_i.query({
    "AoMeasurementQuantity": {
        "name": "Revs"
    },
    "$attributes": {
        "minimum": {
            "$min": 1,
            "$max": 1
        },
        "maximum": {
            "$min": 1,
            "$max": 1
        }
    }
})
```

## Complete Query Example

A comprehensive example with multiple query features:

```python
r = con_i.query({
    "AoMeasurement": {
        "$or": [
            {
                "measurement_begin": {
                    "$gte": "2012-04-23T00:00:00.000Z",
                    "$lt": "2012-04-24T00:00:00.000Z"
                }
            },
            {
                "measurement_begin": {
                    "$gte": "2012-05-23T00:00:00.000Z",
                    "$lt": "2012-05-24T00:00:00.000Z"
                }
            },
            {
                "measurement_begin": {
                    "$gte": "2012-06-23T00:00:00.000Z",
                    "$lt": "2012-06-24T00:00:00.000Z"
                }
            }
        ]
    },
    "$options": {
        "$rowlimit": 1000,
        "$rowskip": 500
    },
    "$attributes": {
        "name": 1,
        "id": 1,
        "test": {
            "name": 1,
            "id": 1
        }
    },
    "$orderby": {
        "test.name": 0,
        "name": 1
    },
    "$groupby": {
        "id": 1
    }
})
```

## Joins

### Outer Join

Use outer joins to retrieve sparse set unit names:

```python
r = con_i.query({
    "AoMeasurementQuantity": {
        "measurement": 4712
    },
    "$attributes": {
        "name": 1,
        "id": 1,
        "datatype": 1,
        "unit:OUTER.name": 1
    }
})
```

**Note**: Outer joins are specified by adding `:OUTER` to the end of a relation name before the next dot.

## Special Key Values

### Query Result Selection

| Key | Description |
|-----|-------------|
| `$attributes` | List of attributes to retrieve |
| `$orderby` | Order results (1=ascending, 0=descending) |
| `$groupby` | Group results by this field |
| `$options` | Global query options |

### Logical Operators

| Operator | Description |
|----------|-------------|
| `$and` | Connect array elements with logical AND |
| `$or` | Connect array elements with logical OR |
| `$not` | Invert result of expression |

### Comparison Operators

| Operator | Description |
|----------|-------------|
| `$eq` | Equal |
| `$neq` | Not equal |
| `$lt` | Less than |
| `$gt` | Greater than |
| `$lte` | Less than or equal |
| `$gte` | Greater than or equal |
| `$in` | Contained in array |
| `$notinset` | Not contained in array |
| `$like` | Equal using wildcards (* ?) |
| `$notlike` | Not equal using wildcards (* ?) |
| `$null` | Is null value |
| `$notnull` | Is not null value |
| `$between` | Between two values (equivalent to `$gte` and `$lt` pair) |
| `$options` | String containing modifiers: `i` for case insensitive |
| `$unit` | Define unit for condition value (0=default unit) |

### Aggregate Functions

| Function | Description |
|----------|-------------|
| `$none` | No aggregate |
| `$count` | Return count of rows |
| `$dcount` | Return count of distinct rows |
| `$min` | Return minimal value |
| `$max` | Return maximal value |
| `$avg` | Return average value |
| `$stddev` | Return standard deviation |
| `$sum` | Return sum of values |
| `$distinct` | Return distinct values |
| `$point` | Query on bulk data, returning indices of local column values |
| `$ia` | Retrieve instance attribute |
| `$unit` | Define unit by ID for return values |
| `$nested` | Assign another Jaquel query to a condition |

### Pagination and Limits

| Option | Description |
|--------|-------------|
| `$rowlimit` | Maximum number of rows to return |
| `$rowskip` | Number of rows to skip |
| `$seqlimit` | Maximum number of entries in a single sequence |
| `$seqskip` | Number of entries to skip in a single sequence |

## Result Naming Modes

### result_naming_mode="query" (Default)

Column names match your JAQUEL query specification exactly:
- Base names and case are reflected (e.g., `name`, `phys_dimension.name`)
- Best for: AI agents, generic programmatic workflows
- Self-documenting: query names tell you how to access them in the DataFrame

### result_naming_mode="model"

Column names use application names from the ODS model:
- Names follow `<entity_name>.<attribute_or_relation_name>` format
- Examples: `Unit.Name`, `PhysDimension.Name`
- Follows ODS model application naming conventions

### Query Result Example

```python
df = con_i.query({
    "AoUnit": {},
    "$attributes": {
        "name": 1,
        "id": 1,
        "factor": 1,
        "phys_dimension.name": 1
    }
}, result_naming_mode="query")
```

Result DataFrame columns:
| Query Name | Model Name | Description |
|------------|-----------|-------------|
| `name` | `Unit.Name` | Unit name |
| `id` | `Unit.Id` | Unit ID |
| `factor` | `Unit.Factor` | Unit factor |
| `phys_dimension.name` | `PhysDimension.Name` | Physical dimension name |

## Important Remarks

- **Enum Values**: Can be given as string or number, but string is case-sensitive
- **LongLong Values**: Can be given as string or number (not all values representable in JSON as numbers)
- **Outer Joins**: Specified by adding `:OUTER` before the next dot in relation names
- **Name Lookup**: Application names are preferred over base names; use them when precision is needed
- **Generic Code**: Use base names for code that should work on any application model

## Related Documentation

- See **Query Operators Reference** for detailed operator information
- Use **Query Execution Patterns** for best practices
- Reference **ODS Entity Hierarchy** for understanding relationships
"""

        else:
            return f"Unknown resource: {uri}"
