"""TOOLS_GUIDE.md - Complete Guide to Jaquel MCP Server Tools."""

# Jaquel MCP Server - Complete Tools Guide

This document provides a comprehensive guide to all tools available in the ASAM ODS Jaquel MCP Server.

## Table of Contents

1. [Overview](#overview)
2. [Tool Reference](#tool-reference)
3. [Common Use Cases](#common-use-cases)
4. [Query Examples](#query-examples)
5. [Operator Reference](#operator-reference)
6. [Tips & Best Practices](#tips--best-practices)

---

## Overview

The Jaquel MCP Server provides tools for working with ASAM ODS Jaquel queries and bulk data access:

### Jaquel Query Tools (10 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| validate_jaquel_query | Validate complete query | Query dict | Validation result |
| get_operator_documentation | Get operator docs | Operator name | Documentation |
| get_query_pattern | Get pattern template | Pattern name | Pattern object |
| list_query_patterns | List all patterns | None | List of patterns |
| generate_query_skeleton | Create query skeleton | Entity name, operation | Query skeleton |
| explain_query | Explain in English | Query dict | Text explanation |

### Schema & Validation Tools (5 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| check_entity_schema | Get entity fields | Entity name | Field list |
| validate_field_exists | Check field (attribute or relationship) exists | Entity name, field name | Validation result |
| debug_query_steps | Break query into steps | Query dict | Debug steps |
| suggest_error_fixes | Get error suggestions | Issue, query | Fix suggestions |

### ODS Connection & Data Access Tools (9 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| connect_ods_server | Connect to ODS server | URL, credentials | Connection status |
| disconnect_ods_server | Disconnect from server | None | Status |
| get_ods_connection_info | Get connection details | None | Connection info |
| list_ods_entities | List all entities | None | Entity list |
| get_test_to_measurement_hierarchy | Get AoTest->AoMeasurement chain | None | Hierarchy chain |
| execute_ods_query | Execute Jaquel query | Query dict | Query results |
| get_submatrix_measurement_quantities | List measurement quantities | Submatrix ID | Quantity list |
| read_submatrix_data | Read timeseries data | Submatrix ID, patterns | DataFrame data |
| generate_submatrix_fetcher_script | Generate Python fetcher scripts | Submatrix ID, script type | Python script |

### Notebook & Visualization Tools (2 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| generate_measurement_comparison_notebook | Generate Jupyter notebook | Query, quantities, ODS credentials | Notebook or .ipynb file |
| generate_plotting_code | Generate matplotlib code | Quantities, count, plot type | Python code string |

### Measurement Analysis & Query Tools (2 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| compare_measurements | Statistical comparison of measurements | Quantity, measurement data | Comparison statistics |
| query_measurement_hierarchy | Explore measurement structure | Query result, operation | Hierarchy info |


---

## Tool Reference

### 1. validate_jaquel_query

**Purpose**: Validate a complete Jaquel query structure.

**Input**:
```json
{
    "query": {
        "EntityName": {...},
        "$attributes": {...}
    }
}
```

**Output**:
```json
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "suggestions": []
}
```

**Checks**:
- ✓ Entity name exists and is non-$key
- ✓ Entity query value is dict, int, or string
- ✓ Special keys ($attributes, $orderby, etc.) are valid
- ✓ $attributes is a dictionary
- ✓ $orderby and $groupby are dictionaries
- ✓ $rowlimit and $rowskip are integers

**Example**:
```python
query = {
    "AoMeasurement": {"name": "Test"},
    "$attributes": {"id": 1, "name": 1},
    "$options": {"$rowlimit": 10}
}
result = JaquelValidator.validate_query(query)
# Returns: {"valid": true, "errors": [], ...}
```

---

### 3. get_operator_documentation

**Purpose**: Get detailed documentation for a Jaquel operator.

**Input**:
```json
{
    "operator": "$eq"
}
```

**Output**:
```json
{
    "category": "comparison",
    "description": "Equal comparison",
    "example": "{\"name\": {\"$eq\": \"MyTest\"}}",
    "options": "Use $options: 'i' for case-insensitive"
}
```

**Supported Operators**:
- Comparison: $eq, $neq, $lt, $gt, $lte, $gte, $in, $like, $between, $null, $notnull
- Logical: $and, $or, $not
- Aggregates: $distinct, $min, $max

**Example**:
```python
doc = JaquelValidator.get_operator_info("$like")
# Returns:
# {
#   "category": "comparison",
#   "description": "Wildcard match (* and ?)",
#   "example": '{"name": {"$like": "Test*"}}',
#   "options": "Use $options: 'i' for case-insensitive"
# }
```

---

### 4. get_query_pattern

**Purpose**: Get a template for a common query pattern.

**Input**:
```json
{
    "pattern": "case_insensitive_search"
}
```

**Output**:
```json
{
    "template": "{\n    \"EntityName\": {\n        \"name\": {\n            \"$like\": \"Search*\",\n            \"$options\": \"i\"\n        }\n    }\n}",
    "description": "Case-insensitive wildcard search",
    "explanation": "$like uses * and ? wildcards. $options: 'i' = case-insensitive"
}
```

**Available Patterns**:
- `get_all_instances` - Get all entities
- `get_by_id` - Get by ID shorthand
- `get_by_name` - Get by name filter
- `case_insensitive_search` - Wildcard search
- `time_range` - Date/time range query
- `inner_join` - Join with related entities
- `outer_join` - Outer join for sparse data
- `aggregates` - Aggregate functions

**Example**:
```python
pattern = JaquelExamples.get_pattern("time_range")
print(pattern["template"])
```

---

### 5. list_query_patterns

**Purpose**: List all available query patterns.

**Input**: None (empty object)

**Output**:
```json
{
    "available_patterns": [
        "get_all_instances",
        "get_by_id",
        "get_by_name",
        "case_insensitive_search",
        "time_range",
        "inner_join",
        "outer_join",
        "aggregates"
    ],
    "description": "Use get_query_pattern tool with one of these names"
}
```

**Example**:
```python
patterns = JaquelExamples.list_patterns()
# Returns list of available pattern names
```

---

### 6. generate_query_skeleton

**Purpose**: Generate a query skeleton for an entity.

**Input**:
```json
{
    "entity_name": "AoMeasurement",
    "operation": "search_and_select"
}
```

**Output**:
```json
{
    "AoMeasurement": {"name": {"$like": "Search*"}},
    "$attributes": {"id": 1, "name": 1, "description": 1},
    "$orderby": {"name": 1},
    "$options": {"$rowlimit": 10}
}
```

**Available Operations**:
- `get_all` - Get all instances (simple)
- `get_by_id` - Query by ID
- `get_by_name` - Query by name
- `search_and_select` - Search with specific attributes

**Example**:
```python
skeleton = JaquelExamples.generate_query_skeleton(
    "AoMeasurement",
    "search_and_select"
)
```

---

### 8. explain_query

**Purpose**: Explain what a query does in plain English.

**Input**:
```json
{
    "query": {
        "AoMeasurement": {"name": "Profile_62"},
        "$attributes": {"id": 1, "name": 1},
        "$orderby": {"name": 1},
        "$options": {"$rowlimit": 10}
    }
}
```

**Output**:
```
Query for entity: AoMeasurement

Filter conditions:
  - name: Profile_62

Attributes to retrieve:
  - id
  - name

Query options:
  - Limit results to 10 rows

Ordering:
  - name: ascending
```

**Example**:
```python
query = {...}
explanation = JaquelExplain.explain_query(query)
print(explanation)
```

---


### 11. check_entity_schema

**Purpose**: Get available fields for an entity from the ODS model schema.

**Input**:
```json
{
    "entity_name": "AoMeasurement"
}
```

**Output**:
```json
{
    "entity_name": "AoMeasurement",
    "fields": [
        {
            "name": "id",
            "type": "integer",
            "description": "Unique identifier"
        },
        {
            "name": "name",
            "type": "string",
            "description": "Measurement name"
        },
        {
            "name": "description",
            "type": "string",
            "description": "Measurement description"
        }
    ],
    "field_count": 3
}
```

**Requirements**: Active ODS server connection.

**Example**:
```python
schema = check_entity_schema("AoMeasurement")
print(f"Entity has {schema['field_count']} fields")
for field in schema['fields']:
    print(f"- {field['name']}: {field['type']}")
```

---

### 12. validate_field_exists

**Purpose**: Check if a field exists in an entity's schema.

**Input**:
```json
{
    "entity_name": "AoMeasurement",
    "field_name": "measurement_begin"
}
```

**Output**:
```json
{
    "entity_name": "AoMeasurement",
    "field_name": "measurement_begin",
    "exists": true,
    "field_info": {
        "type": "datetime",
        "description": "Start time of measurement"
    }
}
```

**Requirements**: Active ODS server connection.

**Example**:
```python
result = validate_field_exists("AoMeasurement", "measurement_begin")
if result["exists"]:
    print(f"Field exists: {result['field_info']['type']}")
else:
    print("Field does not exist")
```

---

### 14. debug_query_steps

**Purpose**: Break down a Jaquel query into logical steps for debugging.

**Input**:
```json
{
    "query": {
        "AoMeasurement": {"name": "Test*"},
        "$attributes": {"id": 1, "name": 1},
        "$orderby": {"name": 1}
    }
}
```

**Output**:
```json
{
    "query_summary": "Query for AoMeasurement entities",
    "steps": [
        {
            "step": 1,
            "operation": "filter",
            "description": "Filter AoMeasurement where name matches 'Test*'",
            "jaquel_fragment": {"AoMeasurement": {"name": "Test*"}}
        },
        {
            "step": 2,
            "operation": "select_attributes",
            "description": "Select id and name attributes",
            "jaquel_fragment": {"$attributes": {"id": 1, "name": 1}}
        },
        {
            "step": 3,
            "operation": "order_by",
            "description": "Order results by name ascending",
            "jaquel_fragment": {"$orderby": {"name": 1}}
        }
    ],
    "estimated_complexity": "simple"
}
```

**Example**:
```python
steps = debug_query_steps(query)
for step in steps["steps"]:
    print(f"Step {step['step']}: {step['description']}")
```

---

### 15. suggest_error_fixes

**Purpose**: Get suggestions to fix common query errors.

**Input**:
```json
{
    "issue": "invalid operator",
    "query": {
        "AoMeasurement": {"name": {"$invalid": "test"}}
    }
}
```

**Output**:
```json
{
    "issue": "invalid operator",
    "query": {
        "AoMeasurement": {"name": {"$invalid": "test"}}
    },
    "suggestions": [
        {
            "fix_type": "operator_correction",
            "description": "Replace $invalid with a valid operator",
            "suggested_fix": {
                "AoMeasurement": {"name": {"$eq": "test"}}
            },
            "confidence": "high"
        },
        {
            "fix_type": "operator_alternatives",
            "description": "Use $like for pattern matching instead",
            "suggested_fix": {
                "AoMeasurement": {"name": {"$like": "test*"}}
            },
            "confidence": "medium"
        }
    ],
    "common_fixes": [
        "$eq for exact match",
        "$like for pattern matching",
        "$in for multiple values"
    ]
}
```

**Example**:
```python
suggestions = suggest_error_fixes("invalid operator", query)
for suggestion in suggestions["suggestions"]:
    print(f"Fix: {suggestion['description']}")
```

---

### 16. connect_ods_server

**Purpose**: Establish connection to ASAM ODS server for live model inspection and data access.

**Input**:
```json
{
    "url": "http://localhost:8087/api",
    "username": "sa",
    "password": "sa"
}
```

**Output**:
```json
{
    "success": true,
    "message": "Connected to ODS server",
    "connection": {
        "url": "http://localhost:8087/api",
        "username": "sa",
        "con_i_url": "http://localhost:8087/api/con_i/12345"
    }
}
```

**Requirements**: Valid ODS server URL and credentials.

---

### 17. disconnect_ods_server

**Purpose**: Close connection to ODS server.

**Input**:
```json
{}
```

**Output**:
```json
{
    "success": true,
    "message": "Disconnected from ODS server"
}
```

---

### 18. get_ods_connection_info

**Purpose**: Get current ODS connection information.

**Input**:
```json
{}
```

**Output**:
```json
{
    "url": "http://localhost:8087/api",
    "username": "sa",
    "con_i_url": "http://localhost:8087/api/con_i/12345",
    "status": "connected"
}
```

---

### 19. list_ods_entities

**Purpose**: Return a list of existing entities from the ODS server ModelCache with their relationships.

**Input**:
```json
{}
```

**Output**:
```json
{
    "entities": [
        {
            "name": "AoUnit",
            "basename": "AoUnit",
            "description": "Represents information about a specific physical unit (e.g., Newton, Kelvin).",
            "related_entities": [
                {
                    "name": "AoQuantity",
                    "relationship": "1:n",
                    "relation_name": "quantity"
                }
            ]
        }
    ],
    "count": 1
}
```

**Requirements**: Must be connected to ODS server first using `connect_ods_server`.

**Entity Information**:
- `name`: Entity name
- `basename`: Base entity name
- `description`: Human-readable description
- `related_entities`: Array of related entities with relationship types (1:n, n:1, n:m)

---

### 20. get_test_to_measurement_hierarchy

**Purpose**: Get the hierarchical entity chain from AoTest to AoMeasurement via the 'children' relation.

This is the main ASAM ODS hierarchy for accessing test data:
- **Root**: AoTest (test campaign or program)
- **Intermediate**: AoSubTest (optional, may appear multiple times)
- **Leaf**: AoMeasurement (individual measurement/test case)

**Input**:
```json
{}
```

**Output**:
```json
{
    "success": true,
    "hierarchy_chain": [
        {
            "name": "Test",
            "base_name": "AoTest",
            "parent_relation": null,
            "description": "The root entity of the test hierarchy representing test campaigns or programs..."
        },
        {
            "name": "SubTest",
            "base_name": "AoSubTest",
            "parent_relation": "parent_test",
            "description": "An intermediate level in the test hierarchy that enables the organization of complex test scenarios..."
        },
        {
            "name": "Measurement",
            "base_name": "AoMeasurement",
            "parent_relation": "test",
            "description": "The primary container for a complete measurement or test case..."
        }
    ],
    "depth": 3,
    "note": "This is the main AoTest to AoMeasurement hierarchy in this ASAM ODS server"
}
```

**Requirements**: Must be connected to ODS server first using `connect_ods_server`.

**Usage**: 
Use this tool to understand the entity hierarchy for building Jaquel queries that navigate from tests down to measurements. This helps LLMs and users understand the proper entity traversal path.

**Example Query Pattern**:
After getting this hierarchy, you can build queries like:
```python
# Navigate from AoTest through hierarchy to AoMeasurement
query = {
    "AoMeasurement": {
        "name": "MyMeas1",
        "test": {
            "name": "SubTest1", 
            "parent_test": {
                "name" : "MyProject1"
            }
        }
    }
}
```

---

### 21. execute_ods_query

**Purpose**: Execute a Jaquel query directly on connected ODS server.

**Input**:
```json
{
    "query": {
        "AoUnit": {},
        "$attributes": {"id": 1, "name": 1}
    }
}
```

**Output**:
```json
{
    "success": true,
    "result": "<DataFrame>",
    "entity_count": 42
}
```

**Note**: Returns DataFrame object (may not be serializable in JSON response).

---

### 22. get_submatrix_measurement_quantities

**Purpose**: Get available measurement quantities for a submatrix.

**Input**:
```json
{
    "submatrix_id": 123
}
```

**Output**:
```json
{
    "submatrix_id": 123,
    "measurement_quantities": [
        {
            "id": 456,
            "name": "Time",
            "measurement_quantity": "Time",
            "unit": "s",
            "sequence_representation": 1,
            "independent": true
        },
        {
            "id": 457,
            "name": "Temperature",
            "measurement_quantity": "Temperature",
            "unit": "°C",
            "sequence_representation": 1,
            "independent": false
        }
    ],
    "count": 2
}
```

**Requirements**: Active ODS server connection.

---

### 22. read_submatrix_data

**Purpose**: Read timeseries data from a submatrix using bulk data access.

**Input**:
```json
{
    "submatrix_id": 123,
    "measurement_quantity_patterns": ["Time", "Temp*"],
    "case_insensitive": false,
    "date_as_timestamp": true,
    "set_independent_as_index": true
}
```

**Output**:
```json
{
    "submatrix_id": 123,
    "columns": ["Time", "Temperature", "Pressure"],
    "row_count": 1000,
    "data_preview": [
        {"Time": 0.0, "Temperature": 25.0, "Pressure": 1013.25},
        {"Time": 0.1, "Temperature": 25.1, "Pressure": 1013.20}
    ],
    "note": "Full DataFrame returned (may be large)"
}
```

**Requirements**: Active ODS server connection.

---

### 23. generate_submatrix_fetcher_script

**Purpose**: Generate Python script examples for fetching submatrix data with proper error handling and data processing.

**Input**:
```json
{
    "submatrix_id": 123,
    "script_type": "basic",
    "measurement_quantity_patterns": ["Time", "Temp*"],
    "output_format": "csv",
    "include_visualization": false,
    "include_analysis": false
}
```

**Output**:
```json
{
    "submatrix_id": 123,
    "script_type": "basic",
    "output_format": "csv",
    "measurement_quantities": ["Time", "Temperature"],
    "script": "#!/usr/bin/env python3\\n... (complete Python script)",
    "instructions": "Copy the script above into a Python file and run it. Make sure to install required packages: pip install odsbox pandas matplotlib seaborn"
}
```

**Script Types**:
- `"basic"`: Simple data fetching script
- `"advanced"`: Full-featured script with logging, error handling, and data validation
- `"batch"`: Script for processing multiple submatrices in parallel
- `"analysis"`: Script with comprehensive data analysis and visualization

**Parameters**:
- `script_type`: Type of script to generate (required)
- `measurement_quantity_patterns`: Column patterns to include (optional, auto-detected if not provided)
- `output_format`: Data output format - "csv", "json", "parquet", "excel", or "dataframe"
- `include_visualization`: Include matplotlib/seaborn plotting code
- `include_analysis`: Include basic statistical analysis

**Requirements**: Active ODS server connection.

**Example Generated Script** (basic type):
```python
#!/usr/bin/env python3
"""
Basic Submatrix Data Fetcher
Fetches data from submatrix 123
"""

import pandas as pd
from odsbox import ConI

def main():
    
    try:
    # Connect to ODS server
        with ConI(url="http://localhost:8087/api",  # Update with your ODS server URL
            auth=("your_username", "your_password")) as con_i:

            # Fetch data from submatrix
            df = con_i.bulk.data_read(
                submatrix_iid=123,
                column_patterns=["Time", "Temp*"],
                date_as_timestamp=True,
                set_independent_as_index=True
            )
        
        print(f"Loaded data with shape: {{df.shape}}")
        print(f"Columns: {{list(df.columns)}}")
        print("\\nFirst 5 rows:")
        print(df.head())
        
        # Save to file
        df.to_csv("submatrix_123_data.csv", index=True)
        print("\\nData saved successfully!")
        
    except Exception as e:
        print(f"Error fetching data: {{e}}")

if __name__ == "__main__":
    main()
```

---

## Common Use Cases

### Use Case 1: Validate User Query

```python
# User provides a query, validate it
user_query = {
    "AoMeasurement": {
        "name": {"$like": "Test*"}
    },
    "$attributes": {"id": 1, "name": 1},
    "$options": {"$rowlimit": 50}
}

result = JaquelValidator.validate_query(user_query)
if result["valid"]:
    print("Query is valid!")
else:
    print("Errors:", result["errors"])
```

### Use Case 3: Learn Operator Usage

```python
# User wants to know how to use an operator
doc = JaquelValidator.get_operator_info("$between")
print(f"Description: {doc['description']}")
print(f"Example: {doc['example']}")
```

### Use Case 4: Generate Query from Scratch

```python
# Generate template, then customize it
skeleton = JaquelExamples.generate_query_skeleton(
    "AoMeasurement",
    "search_and_select"
)

# Modify skeleton as needed
skeleton["AoMeasurement"]["name"] = {"$like": "Profile*"}
skeleton["$options"]["$rowlimit"] = 5

# Validate
result = JaquelValidator.validate_query(skeleton)
```

---

## Query Examples

### Example 1: Simple ID Lookup

```json
{
    "AoMeasurement": 4711
}
```

### Example 2: Name Search

```json
{
    "AoMeasurement": {
        "name": {"$like": "Profile*", "$options": "i"}
    },
    "$attributes": {"id": 1, "name": 1},
    "$options": {"$rowlimit": 10}
}
```

### Example 3: Time Range Query

```json
{
    "AoMeasurement": {
        "measurement_begin": {
            "$between": ["2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z"]
        }
    },
    "$attributes": {"id": 1, "name": 1, "measurement_begin": 1}
}
```

### Example 4: Multiple Conditions

```json
{
    "AoMeasurement": {
        "$and": [
            {"status": "active"},
            {"measurement_begin": {"$gte": "2023-01-01T00:00:00Z"}},
            {"measurement_end": {"$lte": "2023-12-31T23:59:59Z"}}
        ]
    },
    "$attributes": {"id": 1, "name": 1},
    "$orderby": {"measurement_begin": 0}
}
```

### Example 5: Inner Join

```json
{
    "AoMeasurementQuantity": {},
    "$attributes": {
        "name": 1,
        "unit.name": 1,
        "quantity.name": 1
    },
    "$options": {"$rowlimit": 5}
}
```

### Example 6: Outer Join

```json
{
    "AoMeasurementQuantity": {},
    "$attributes": {
        "name": 1,
        "unit:OUTER.name": 1,
        "quantity:OUTER.name": 1
    }
}
```

### Example 7: Aggregates

```json
{
    "AoUnit": {},
    "$attributes": {
        "factor": {"$min": 1, "$max": 1, "$avg": 1},
        "description": {"$distinct": 1, "$dcount": 1}
    }
}
```

---

## Operator Reference

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equal | `{"name": {"$eq": "Test"}}` |
| `$neq` | Not equal | `{"status": {"$neq": "inactive"}}` |
| `$lt` | Less than | `{"value": {"$lt": 100}}` |
| `$gt` | Greater than | `{"value": {"$gt": 0}}` |
| `$lte` | Less or equal | `{"value": {"$lte": 100}}` |
| `$gte` | Greater or equal | `{"value": {"$gte": 0}}` |
| `$in` | In array | `{"id": {"$in": [1, 2, 3]}}` |
| `$like` | Wildcard match | `{"name": {"$like": "Test*"}}` |
| `$between` | Between values | `{"date": {"$between": [..., ...]}}` |
| `$null` | Is null | `{"field": {"$null": 1}}` |
| `$notnull` | Not null | `{"field": {"$notnull": 1}}` |

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$and` | Logical AND | `{"$and": [{...}, {...}]}` |
| `$or` | Logical OR | `{"$or": [{...}, {...}]}` |
| `$not` | Logical NOT | `{"$not": {...}}` |

### Aggregate Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$min` | Minimum value | `{"field": {"$min": 1}}` |
| `$max` | Maximum value | `{"field": {"$max": 1}}` |
| `$avg` | Average value | `{"field": {"$avg": 1}}` |
| `$count` | Count rows | `{"field": {"$count": 1}}` |
| `$dcount` | Distinct count | `{"field": {"$dcount": 1}}` |
| `$distinct` | Unique values | `{"field": {"$distinct": 1}}` |
| `$sum` | Sum values | `{"field": {"$sum": 1}}` |
| `$stddev` | Standard deviation | `{"field": {"$stddev": 1}}` |

### Special Options

| Key | Description | Example |
|-----|-------------|---------|
| `$attributes` | Select attributes | `{"$attributes": {"id": 1}}` |
| `$orderby` | Sort results | `{"$orderby": {"name": 1}}` |
| `$groupby` | Group results | `{"$groupby": {"id": 1}}` |
| `$options` | Query options | `{"$options": {"$rowlimit": 10}}` |
| `$unit` | Specify unit | `{"$unit": 123}` |

---

## Tips & Best Practices

### 1. Always Validate Before Using

```python
result = JaquelValidator.validate_query(query)
if not result["valid"]:
    raise ValueError(result["errors"])
```

### 2. Use Patterns as Starting Points

```python
# Start with a pattern, then customize
pattern = JaquelExamples.get_pattern("time_range")
query = json.loads(pattern["template"])
# Modify as needed
```

### 3. Use Case-Insensitive for User Searches

```python
# Bad: Case-sensitive, might miss data
{"name": "TestProfile"}

# Good: Case-insensitive with wildcard
{"name": {"$like": "Test*", "$options": "i"}}
```

### 4. Set Row Limits for Large Queries

```python
# Good: Prevents large result sets
"$options": {"$rowlimit": 1000}

# Better: Combine with paging
"$options": {"$rowlimit": 1000, "$rowskip": 0}
```

### 5. Use Inner Joins for Required Data

```python
# Inner join - related data must exist
"unit.name": 1

# Outer join - handles missing related data
"unit:OUTER.name": 1
```

### 6. Simplify Verbose Queries

```python
# Verbose
{"AoUnit": {"id": {"$eq": 123}}}

# Simplified
{"AoUnit": 123}
```

### 7. Document Complex Conditions

```python
# Use explain_query to understand queries
explanation = JaquelExplain.explain_query(complex_query)
print(explanation)  # Share with team for clarity
```

### 8. Test Operators Before Using

```python
# Verify operator syntax
info = JaquelValidator.get_operator_info("$like")
print(info["example"])  # See correct usage
```

### 9. Use Explicit $and for Complex Logic

```python
# Better for readability
"$and": [
    {"status": "active"},
    {"value": {"$gte": 100}},
    {"date": {"$gt": "2023-01-01"}}
]

# Instead of nested conditions
```

---

## Error Handling

### Common Validation Errors

```python
# Missing entity name
{
    "$attributes": {"id": 1}
}
# Error: "Query must contain an entity name (non-$ key)"

# Invalid $rowlimit
{
    "AoUnit": {},
    "$options": {"$rowlimit": "10"}
}
# Error: "$rowlimit must be an integer"

# Unknown operator
{
    "name": {"$invalid": "value"}
}
# Error: "Unknown operator: $invalid"
```

### Debugging Tips

1. **Use validate_jaquel_query** to find syntax errors
2. **Use explain_query** to understand complex queries
3. **Use get_operator_documentation** to verify operator syntax
4. **Use suggest_optimizations** to find issues and improvements

---

## Notebook & Visualization Tools (NEW)

### 24. generate_measurement_comparison_notebook

**Purpose**: Generate a complete Jupyter notebook for comparing measurements with automatic data retrieval, preparation, and visualization.

**Input**:
```json
{
    "measurement_query_conditions": {
        "Name": {"$like": "Profile_*"},
        "TestStep.Test.Name": {"$in": ["Campaign_03", "Campaign_04"]}
    },
    "measurement_quantity_names": ["Motor_speed", "Torque"],
    "ods_url": "https://ods.example.com/api",
    "ods_username": "user",
    "ods_password": "password",
    "available_quantities": ["Motor_speed", "Torque", "Temperature", "Coolant"],
    "plot_type": "scatter",
    "title": "Motor Performance Comparison",
    "output_path": "/path/to/notebook.ipynb"
}
```

**Output**:
```json
{
    "title": "Motor Performance Comparison",
    "plot_type": "scatter",
    "measurement_quantities": ["Motor_speed", "Torque"],
    "num_cells": 9,
    "status": "Notebook generated successfully",
    "saved_to": "/path/to/notebook.ipynb"
}
```

**Features**:
- ✓ Query definition cell with ODS credentials
- ✓ Data retrieval code using odsbox library
- ✓ Automatic data preparation with helper functions
- ✓ Matplotlib visualization code
- ✓ Configurable plot types: scatter, line, or subplots
- ✓ Unit extraction and label formatting
- ✓ Optional file output

**Plot Types**:
- `scatter` - 2D scatter plots with independent column as color mapping
- `line` - Multi-line time series plots
- `subplots` - Separate subplots for each quantity

**Example Generated Notebook Structure**:
1. Title and description
2. Available quantities documentation
3. Query definition cell
4. ODS data retrieval code
5. Data preparation with helper functions
6. Visualization code

---

### 25. generate_plotting_code

**Purpose**: Generate standalone matplotlib plotting code for measurement visualization.

**Input**:
```json
{
    "measurement_quantity_names": ["Speed", "Torque", "Temperature"],
    "submatrices_count": 6,
    "plot_type": "line"
}
```

**Output**:
```json
{
    "plot_type": "line",
    "measurement_quantities": ["Speed", "Torque", "Temperature"],
    "submatrices_count": 6,
    "code": "import matplotlib.pyplot as plt\n...",
    "description": "Generated line plot code for 3 quantities and 6 submatrices"
}
```

**Plot Types**:

**Scatter Plot** (requires 2+ quantities):
- 2D scatter plots
- Color mapping by independent column (e.g., time)
- Configurable subplot layout (default: 3 per row)
- Automatic axis labeling

**Line Plot** (any number of quantities):
- Multiple line series per plot
- Legend, grid, and marker styling
- Configurable subplot layout
- Good for time series data

**Subplots Per Measurement**:
- One subplot row per quantity
- Multiple columns for each measurement
- Best for detailed quantity-by-measurement analysis

**Example**:
```python
code = generate_plotting_code(
    measurement_quantity_names=["Speed", "Torque"],
    submatrices_count=9,
    plot_type="scatter"
)
# Returns executable matplotlib code
```

---

## Integration Examples

### With Python odsbox Library

```python
from odsbox import ConI
from odsbox_jaquel_mcp import JaquelValidator

# Build and validate query
query = {
    "AoMeasurement": {"name": "Profile_62"},
    "$attributes": {"id": 1, "name": 1}
}

result = JaquelValidator.validate_query(query)
if result["valid"]:
    # Use with odsbox
    with ConI(...) as con_i:
        data = con_i.query(query)
```

### With AI Assistants (Claude)

```
User: "Help me create a query for all measurements in 2023"

Assistant uses tools:
1. list_query_patterns() → Shows available patterns
2. get_query_pattern("time_range") → Gets time range template
3. generate_query_skeleton("AoMeasurement", "get_all") → Creates skeleton
4. suggest_optimizations() → Cleans up the query
5. explain_query() → Explains the result
```

---

## Measurement Analysis & Query Tools (NEW)

### 26. compare_measurements

**Purpose**: Compare measurements across quantities with statistical analysis.

**Input**:
```json
{
    "quantity_name": "Motor_speed",
    "measurement_data": {
        "1": [50, 55, 52, 51, 54],
        "2": [52, 56, 53, 52, 55],
        "3": [48, 50, 49, 51, 47]
    },
    "measurement_names": {
        "1": "Campaign_A",
        "2": "Campaign_B",
        "3": "Campaign_C"
    }
}
```

**Output**:
```json
{
    "quantity_name": "Motor_speed",
    "num_measurements": 3,
    "measurement_ids": [1, 2, 3],
    "statistics_by_measurement": {
        "1": {
            "name": "Motor_speed",
            "count": 5,
            "mean": 52.4,
            "median": 52.0,
            "stdev": 1.67,
            "min": 50.0,
            "max": 55.0,
            "range": 5.0
        }
    },
    "overall_statistics": {
        "mean": 51.73,
        "median": 51.5,
        "stdev": 2.14
    },
    "pairwise_comparisons": [
        {
            "quantity_name": "Motor_speed",
            "measurement_1_id": 1,
            "measurement_2_id": 2,
            "measurement_1_mean": 52.4,
            "measurement_2_mean": 52.6,
            "mean_difference": 0.2,
            "mean_difference_percent": 0.38,
            "correlation": 0.98,
            "notes": ["Strong positive correlation detected"]
        }
    ],
    "summary": {
        "significant_differences_found": 0,
        "strong_correlations_found": 2
    }
}
```

**Features**:
- ✓ Calculate statistics per measurement (mean, median, stdev, range)
- ✓ Pairwise comparisons between measurements
- ✓ Correlation coefficient calculation
- ✓ Detect significant differences (>10%)
- ✓ Identify strong correlations (>0.95)
- ✓ Generate comparison summary

**Parameters**:
- `quantity_name` (required): Name of quantity to compare
- `measurement_data` (required): Dict mapping measurement_id to list of values
- `measurement_names` (optional): Dict mapping measurement_id to display names

**Use Cases**:
- Compare engine performance across multiple test runs
- Analyze consistency of measurements across campaigns
- Detect correlations between measurements
- Identify outliers or anomalies

---

### 27. query_measurement_hierarchy

**Purpose**: Query and explore ODS measurement hierarchy and structure.

**Input** (Extract Measurements):
```json
{
    "query_result": {
        "AoMeasurement": [
            {"Id": 1, "Name": "Meas_001", "TestName": "Test1"},
            {"Id": 2, "Name": "Meas_002", "TestName": "Test1"}
        ]
    },
    "operation": "extract_measurements"
}
```

**Output** (Extract Measurements):
```json
{
    "operation": "extract_measurements",
    "num_measurements": 2,
    "measurements": [
        {"Id": 1, "Name": "Meas_001", "TestName": "Test1"},
        {"Id": 2, "Name": "Meas_002", "TestName": "Test1"}
    ]
}
```

**Input** (Build Hierarchy):
```json
{
    "query_result": {...},
    "operation": "build_hierarchy"
}
```

**Output** (Build Hierarchy):
```json
{
    "operation": "build_hierarchy",
    "hierarchy_keys": ["by_test", "by_date_range", "by_status", "total_measurements"],
    "total_measurements": 42,
    "tests": ["ProfileTest", "AccelerationTest", "BrakingTest"],
    "statuses": ["Complete", "Incomplete", "Failed"]
}
```

**Input** (Get Unique Tests):
```json
{
    "query_result": {...},
    "operation": "get_unique_tests"
}
```

**Output** (Get Unique Tests):
```json
{
    "operation": "get_unique_tests",
    "unique_tests": ["AccelerationTest", "BrakingTest", "ProfileTest"],
    "num_tests": 3
}
```

**Input** (Get Unique Quantities):
```json
{
    "query_result": {...},
    "operation": "get_unique_quantities"
}
```

**Output** (Get Unique Quantities):
```json
{
    "operation": "get_unique_quantities",
    "unique_quantities": ["Current", "Speed", "Temperature", "Torque"],
    "num_quantities": 4
}
```

**Input** (Build Index):
```json
{
    "query_result": {...},
    "operation": "build_index"
}
```

**Output** (Build Index):
```json
{
    "operation": "build_index",
    "total_measurements": 42,
    "index_by_id_count": 42,
    "index_by_name_count": 40,
    "index_by_test_count": 3,
    "index_by_status_count": 2,
    "available_test_names": ["AccelerationTest", "BrakingTest", "ProfileTest"]
}
```

**Operations**:
- `extract_measurements`: Extract measurement objects from query result
- `build_hierarchy`: Organize measurements by test, status, etc.
- `get_unique_tests`: List all unique test names
- `get_unique_quantities`: List all unique measurement quantities
- `build_index`: Create fast lookup index by multiple keys

**Parameters**:
- `query_result` (required): ODS query result to explore
- `operation` (required): Operation to perform (see list above)
- `test_name` (optional): Filter by test name
- `quantity_names` (optional): Filter by quantities

**Use Cases**:
- Discover available tests and measurements
- Explore what quantities are available
- Find measurements by test type
- Build quick lookup structures
- Understand measurement organization

---

## AI Guidance Tools (NEW)

### 28. get_bulk_api_help

**Purpose**: Get contextual help on bulk API usage for loading timeseries data efficiently. This tool provides step-by-step guidance for AI models learning to use the bulk data access system.

**Input**:
```json
{
    "topic": "the_3_step_rule",
    "tool": "read_submatrix_data"
}
```

**Output**:
```json
{
    "topic": "the_3_step_rule",
    "help_text": "The bulk API follows a 3-step workflow:\n\n1. CONNECT: Establish ODS connection with connect_ods_server\n   - URL: ODS server API endpoint\n   - Credentials: username/password for authentication\n\n2. DISCOVER: Find submatrix IDs and quantities\n   - List measurements with execute_ods_query\n   - Get quantities with get_submatrix_measurement_quantities\n   - Explore hierarchy with query_measurement_hierarchy\n\n3. LOAD: Read timeseries data efficiently\n   - Use read_submatrix_data for bulk data access\n   - Specify column patterns for filtering\n   - Get DataFrame with all rows instantly\n\nKey Benefits:\n- No pagination loops needed - all data loaded at once\n- Column filtering reduces memory usage\n- Pattern matching for flexible column selection\n- Automatic format conversion (dates, etc.)",
    "examples_count": 3,
    "related_tools": ["connect_ods_server", "get_submatrix_measurement_quantities", "read_submatrix_data"]
}
```

**Available Topics**:

1. **the_3_step_rule** - Core workflow: CONNECT → DISCOVER → LOAD
   - Explains fundamental pattern
   - Shows when to use each step
   - Includes decision points

2. **bulk_vs_jaquel** - When to use bulk API vs Jaquel queries
   - Bulk: Fast for known measurements, loads all data at once
   - Jaquel: For discovery, filtering, complex queries
   - Decision tree for tool selection

3. **pattern_syntax** - Column matching patterns
   - Wildcard patterns: `"Time*"`, `"*Temp*"`, `"*Speed"`
   - Exact match: `"Temperature"`
   - Multiple patterns: `["Time", "Motor_*", "*Pressure"]`
   - Case sensitivity options

4. **common_mistakes** - Top 5 AI mistakes and fixes
   - Trying to query metadata with bulk API
   - Forgetting to connect first
   - Using wrong column names
   - Not using pattern matching for flexibility
   - Attempting pagination on bulk data

5. **decision_tree** - How to choose the right approach
   - "I know measurement IDs" → Use bulk API
   - "I need to search" → Use Jaquel first
   - "I want timeseries data" → Bulk API after discovery
   - "I need to filter" → Combine Jaquel + bulk

6. **quick_start** - 5-minute getting started guide
   - Import statements
   - Connection code
   - Discovery code
   - Data loading code
   - Basic error handling

7. **column_patterns** - Advanced pattern matching
   - Wildcard examples
   - Regular expressions (if supported)
   - Case-insensitive matching
   - Filtering for performance

8. **error_handling** - Common errors and recovery
   - "Submatrix not found" - Check measurement IDs
   - "No quantities available" - Verify connected and ID is valid
   - "Pattern matches nothing" - Review available quantity names
   - Timeout issues and workarounds

9. **performance_tips** - Optimize data loading
   - Use patterns to filter columns
   - Index selection for faster access
   - Batch processing for multiple measurements
   - Memory management

10. **tool_comparison** - Bulk API vs odsbox library
    - When to use MCP tools vs direct library
    - Integration patterns
    - Trade-offs and benefits

11. **workflow_examples** - Complete workflows
    - Find and load a measurement
    - Compare multiple measurements
    - Process measurement hierarchy
    - Generate analysis notebook

**Parameters**:

- `topic` (required): Help topic to retrieve. One of:
  - `"the_3_step_rule"` - Core workflow
  - `"bulk_vs_jaquel"` - Tool selection
  - `"pattern_syntax"` - Column patterns
  - `"common_mistakes"` - Error avoidance
  - `"decision_tree"` - Decision making
  - `"quick_start"` - Getting started
  - `"column_patterns"` - Advanced patterns
  - `"error_handling"` - Error recovery
  - `"performance_tips"` - Optimization
  - `"tool_comparison"` - MCP vs library
  - `"workflow_examples"` - Complete workflows

- `tool` (optional): Get contextual help for a specific tool:
  - `"connect_ods_server"` - Connection help
  - `"read_submatrix_data"` - Data loading help
  - `"get_submatrix_measurement_quantities"` - Discovery help
  - `"generate_submatrix_fetcher_script"` - Script generation help
  - `"query_measurement_hierarchy"` - Hierarchy exploration help

**Examples**:

### Get fundamental workflow:
```python
result = get_bulk_api_help(topic="the_3_step_rule")
print(result["help_text"])
# Returns: CONNECT → DISCOVER → LOAD workflow with benefits
```

### Get contextual help for specific tool:
```python
result = get_bulk_api_help(
    topic="quick_start",
    tool="read_submatrix_data"
)
# Returns: Quick start guide with data loading focus
```

### Decide between tools:
```python
result = get_bulk_api_help(topic="decision_tree")
# Returns: Decision tree for tool selection
```

### Learn error recovery:
```python
result = get_bulk_api_help(topic="error_handling")
# Returns: Common errors and how to fix them
```

**Use Cases**:

1. **AI Learning**: When AI model encounters bulk API for first time
   - Call: `get_bulk_api_help(topic="the_3_step_rule")`
   - Then: Follow the 3-step pattern

2. **Tool Selection**: Unsure whether to use bulk or Jaquel
   - Call: `get_bulk_api_help(topic="decision_tree")`
   - Then: Choose appropriate approach

3. **Error Recovery**: Data loading failed
   - Call: `get_bulk_api_help(topic="error_handling")`
   - Then: Apply suggested fix

4. **Pattern Matching**: Unsure about column selection
   - Call: `get_bulk_api_help(topic="column_patterns")`
   - Then: Use correct pattern syntax

5. **Performance**: Need to optimize data loading
   - Call: `get_bulk_api_help(topic="performance_tips")`
   - Then: Apply optimization

**Documentation Links**:

For comprehensive documentation on bulk API usage, see:
- [`00_START_HERE.md`](00_START_HERE.md) - Main entry point
- [`BULK_API_README.md`](BULK_API_README.md) - Complete navigation guide
- [`BULK_API_USAGE_GUIDE.md`](BULK_API_USAGE_GUIDE.md) - In-depth usage guide
- [`BULK_API_QUICK_REF.md`](BULK_API_QUICK_REF.md) - Quick reference card
- [`BULK_API_EXAMPLES.md`](BULK_API_EXAMPLES.md) - 8+ complete workflows
- [`BULK_API_AI_PROMPT.md`](BULK_API_AI_PROMPT.md) - AI system prompt

---

## Additional Resources

- [Jaquel Documentation](https://peak-solution.github.io/odsbox/jaquel.html)
- [Jaquel Examples](https://peak-solution.github.io/odsbox/jaquel_examples.html)
- [ODSBox GitHub](https://github.com/peak-solution/odsbox)
- [ASAM ODS Standard](https://www.asam.net/)
- [Bulk API Guides](BULK_API_README.md) - Learn efficient timeseries data loading

---

**Last Updated**: October 2025
**Version**: 1.1.0 (Added bulk API guidance tools)
