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
| validate_filter_condition | Validate WHERE clause | Condition dict | Validation result |
| get_operator_documentation | Get operator docs | Operator name | Documentation |
| suggest_optimizations | Find improvements | Query dict | List of suggestions |
| get_query_pattern | Get pattern template | Pattern name | Pattern object |
| list_query_patterns | List all patterns | None | List of patterns |
| generate_query_skeleton | Create query skeleton | Entity name, operation | Query skeleton |
| build_filter_condition | Build condition | Field, operator, value | Condition dict |
| explain_jaquel_query | Explain in English | Query dict | Text explanation |
| merge_filter_conditions | Combine conditions | Conditions array, operator | Merged condition |

### Schema & Validation Tools (5 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| check_entity_schema | Get entity fields | Entity name | Field list |
| validate_field_exists | Check field exists | Entity name, field name | Validation result |
| validate_filter_against_schema | Validate filter vs schema | Entity name, filter | Validation result |
| debug_query_steps | Break query into steps | Query dict | Debug steps |
| suggest_error_fixes | Get error suggestions | Issue, query | Fix suggestions |

### ODS Connection & Data Access Tools (8 tools)
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| connect_ods_server | Connect to ODS server | URL, credentials | Connection status |
| disconnect_ods_server | Disconnect from server | None | Status |
| get_ods_connection_info | Get connection details | None | Connection info |
| list_ods_entities | List all entities | None | Entity list |
| execute_ods_query | Execute Jaquel query | Query dict | Query results |
| get_submatrix_measurement_quantities | List measurement quantities | Submatrix ID | Quantity list |
| read_submatrix_data | Read timeseries data | Submatrix ID, patterns | DataFrame data |
| generate_submatrix_fetcher_script | Generate Python fetcher scripts | Submatrix ID, script type | Python script |

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

### 2. validate_filter_condition

**Purpose**: Validate a WHERE clause filter condition.

**Input**:
```json
{
    "condition": {
        "field": {"$operator": value}
    },
    "field_name": "optional_field_name"
}
```

**Output**:
```json
{
    "valid": true,
    "errors": [],
    "issues": []
}
```

**Checks**:
- ✓ Condition is a dictionary
- ✓ Operators are recognized ($eq, $like, $between, etc.)
- ✓ Logical operators ($and, $or, $not) have correct structure
- ✓ $null/$notnull have value 1
- ✓ $between/$in require list values

**Example**:
```python
condition = {
    "measurement_begin": {
        "$between": ["2023-01-01", "2023-12-31"]
    }
}
result = JaquelValidator.validate_filter_condition(condition)
# Returns: {"valid": true, "errors": [], "issues": []}
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

### 4. suggest_optimizations

**Purpose**: Find opportunities to simplify or optimize a query.

**Input**:
```json
{
    "query": {
        "AoUnit": {"id": {"$eq": 123}},
        "$attributes": {}
    }
}
```

**Output**:
```json
{
    "query_summary": "Query for entity: AoUnit",
    "suggestions": [
        "Can simplify: {\"id\": {\"$eq\": 123}} → 123",
        "$attributes is empty - consider removing it"
    ]
}
```

**Optimization Suggestions**:
- Simplify verbose $eq to shorthand
- Use ID shorthand (`EntityName: 123`)
- Remove empty $attributes
- Simplify nested paths

**Example**:
```python
query = {
    "AoUnit": {"id": {"$eq": 456}},
    "$attributes": {}
}
result = JaquelOptimizer.suggest_simplifications(query)
# Suggests: Can use {\"AoUnit\": 456} directly
```

---

### 5. get_query_pattern

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

### 6. list_query_patterns

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

### 7. generate_query_skeleton

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

### 8. build_filter_condition

**Purpose**: Build a filter condition programmatically.

**Input**:
```json
{
    "field": "measurement_begin",
    "operator": "$gte",
    "value": "2023-01-01T00:00:00Z",
    "case_insensitive": false
}
```

**Output**:
```json
{
    "measurement_begin": {
        "$gte": "2023-01-01T00:00:00Z"
    }
}
```

**Operators Supported**:
- All comparison operators: $eq, $neq, $lt, $gt, $lte, $gte, $in, $like, $notlike, $between, $null, $notnull

**Example**:
```python
# Build a time range condition
condition = build_filter_condition(
    field="measurement_begin",
    operator="$gte",
    value="2023-01-01T00:00:00Z"
)
```

---

### 9. explain_jaquel_query

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
explanation = _explain_query(query)
print(explanation)
```

---

### 10. merge_filter_conditions

**Purpose**: Merge multiple filter conditions with AND/OR logic.

**Input**:
```json
{
    "conditions": [
        {"status": "active"},
        {"value": {"$gte": 0}},
        {"value": {"$lte": 100}}
    ],
    "operator": "$and"
}
```

**Output**:
```json
{
    "$and": [
        {"status": "active"},
        {"value": {"$gte": 0}},
        {"value": {"$lte": 100}}
    ]
}
```

**Operators**: `$and`, `$or`

**Example**:
```python
conditions = [
    {"status": "active"},
    {"value": {"$gte": 0}}
]
merged = merge_filter_conditions(conditions, "$and")
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

### 13. validate_filter_against_schema

**Purpose**: Validate a filter condition against the actual entity schema.

**Input**:
```json
{
    "entity_name": "AoMeasurement",
    "filter_condition": {
        "measurement_begin": {"$gte": "2023-01-01"}
    }
}
```

**Output**:
```json
{
    "entity_name": "AoMeasurement",
    "filter_condition": {
        "measurement_begin": {"$gte": "2023-01-01"}
    },
    "valid": true,
    "field_validations": [
        {
            "field": "measurement_begin",
            "exists": true,
            "type": "datetime",
            "operator_valid": true
        }
    ],
    "warnings": [],
    "errors": []
}
```

**Requirements**: Active ODS server connection.

**Example**:
```python
filter_cond = {"measurement_begin": {"$gte": "2023-01-01"}}
result = validate_filter_against_schema("AoMeasurement", filter_cond)
if result["valid"]:
    print("Filter is valid against schema")
else:
    print("Validation errors:", result["errors"])
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

### 20. execute_ods_query

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

### 21. get_submatrix_measurement_quantities

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

### Use Case 2: Build Complex Filter

```python
# Build a complex filter step-by-step
from odsbox_jaquel_mcp import merge_filter_conditions

conditions = [
    build_filter_condition("status", "$eq", "active"),
    build_filter_condition("value", "$gte", 100),
    build_filter_condition("date", "$between", ["2023-01-01", "2023-12-31"])
]

merged = merge_filter_conditions(conditions, "$and")
# Use merged in query
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

### Use Case 5: Optimize Existing Query

```python
# Find opportunities to simplify a query
verbose_query = {
    "AoUnit": {"id": {"$eq": 123}},
    "$attributes": {"id": 1, "name": 1}
}

suggestions = JaquelOptimizer.suggest_simplifications(verbose_query)
for suggestion in suggestions:
    print(suggestion)
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
# Use explain_jaquel_query to understand queries
explanation = _explain_query(complex_query)
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

### 10. Merge Related Conditions

```python
# Use merge_filter_conditions for clean code
conditions = [cond1, cond2, cond3]
merged = merge_filter_conditions(conditions, "$and")
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
2. **Use explain_jaquel_query** to understand complex queries
3. **Use get_operator_documentation** to verify operator syntax
4. **Use suggest_optimizations** to find issues and improvements

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
5. explain_jaquel_query() → Explains the result
```

---

## Additional Resources

- [Jaquel Documentation](https://peak-solution.github.io/odsbox/jaquel.html)
- [Jaquel Examples](https://peak-solution.github.io/odsbox/jaquel_examples.html)
- [ODSBox GitHub](https://github.com/peak-solution/odsbox)
- [ASAM ODS Standard](https://www.asam.net/)

---

**Last Updated**: October 2025
**Version**: 1.0.0
