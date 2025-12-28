# Jaquel Syntax Guide

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
