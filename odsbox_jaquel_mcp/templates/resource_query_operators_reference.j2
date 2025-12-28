# Jaquel Query Operators Reference

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
