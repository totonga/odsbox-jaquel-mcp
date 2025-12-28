# ODS Entity Hierarchy Reference

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
Use query_execute with:
- Entity: AoTest
- Optional filters: name
```

### Finding Measurements
```
Use schema_test_to_measurement_hierarchy to understand relationships
Then navigate: AoTest -> AoSubTest -> AoMeasurement -> AoMeasurementQuantity
```

### Entity Field Names
Use `schema_get_entity` to see all available fields:
- Returns field names, types, and descriptions
- Use for building accurate filter conditions
- Validate field existence with `schema_field_exists`
