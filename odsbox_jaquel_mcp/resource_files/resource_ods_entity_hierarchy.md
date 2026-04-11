# ODS Entity Hierarchy Reference

## Entity Relationships

ASAM ODS uses a hierarchical structure for organizing measurements:

```
AoTest (Test/Measurement Run)
  └─ AoSubTest (Test Group/Step)
      └─ AoMeasurement (Measurement Result)
          └─ AoSubMatrix (Submatrix — bulk data container, carries the submatrix_id)
              └─ AoLocalColumn / AoMeasurementQuantity (Individual timeseries column)
```

> **Key**: `AoSubMatrix.id` is the `submatrix_id` required by `data_get_quantities` and `data_read_submatrix`. Always extract it from `query_execute` results before calling the bulk data tools.

## Common Entities

### AoTest
- **Purpose**: Represents a complete test/measurement run
- **Fields**: name
- **Usage**: Filter and search for specific tests
- **Example**: "Engine_Test_2024_01_15"

### AoSubTest
- **Purpose**: Groups related measurements within a test
- **Fields**: name
- **Usage**: Organize measurements by phase or condition
- **Example**: "Warmup_Phase", "Load_Test"

### AoMeasurement
- **Purpose**: Individual measurement instance
- **Fields**: name, measurement_begin, measurement_end
- **Usage**: Access individual time series data
- **Example**: "TemperatureMeasurement", "PressureMeasurement"

### AoSubMatrix
- **Purpose**: Groups the timeseries columns of one measurement result; carries the numeric ID needed for bulk data access
- **Fields**: id, name
- **Usage**: Extract `id` from query results, then pass it to `data_get_quantities` and `data_read_submatrix`
- **Example**: submatrix_id = 42

### AoLocalColumn / AoMeasurementQuantity
- **Purpose**: Metadata descriptor for a single timeseries column (name, unit, datatype)
- **Fields**: name, unit, datatype, independent (true for the time/index axis)
- **Usage**: Listed by `data_get_quantities`; use the returned names as `measurement_quantity_patterns`
- **Note**: Raw values are not stored as entity fields — they live in external bulk files and are accessed exclusively through `data_read_submatrix`

## Navigating the Hierarchy

### Finding Tests
```
Use query_execute with:
- Entity: AoTest
- Optional filters: name
```

### Finding Measurements and SubMatrix IDs
```
Use schema_test_to_measurement_hierarchy to understand relationships
Then navigate: AoTest -> AoSubTest -> AoMeasurement -> AoSubMatrix
Extract AoSubMatrix.id → use as submatrix_id in data_get_quantities / data_read_submatrix
```

### Entity Field Names
Use `schema_get_entity` to see all available fields:
- Returns field names, types, and descriptions
- Use for building accurate filter conditions
- Validate field existence with `schema_field_exists`
