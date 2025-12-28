# Query Execution Patterns

## Pattern 1: Simple Data Fetch

**When**: You want all data of a specific type

```jaquel
{
  "MeaResult": {},
  "$options": {"$rowlimit": 1000}
}
```

**Use**: `query_execute` directly
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
1. Validate with `query_validate`
2. Execute with `query_execute`

## Pattern 3: Bulk Data Access (Timeseries)

**When**: You need large timeseries datasets

**Steps**:
1. First, get measurement IDs: `query_execute`
2. Extract submatrix IDs from results
3. Use `data_read_submatrix` instead of fetching individual points

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
1. Validate structure: `query_validate`
2. Execute: `query_execute`

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

## Performance Tips

1. **Use Filters Early**: Filter at entity level, not after fetching
2. **Prefer Bulk API**: For timeseries data, use `data_read_submatrix`
3. **Pattern Matching**: In `data_read_submatrix`, use patterns to limit columns
4. **Pagination**: For large result sets, implement server-side pagination
