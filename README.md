
# ASAM ODS Jaquel MCP Server

![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![Status](https://img.shields.io/badge/status-experimental-orange)

**A Model Context Protocol (MCP) server for ASAM ODS with Jaquel query tools, ODS connection management, and bulk data access.**

---

## Features

- 🚀 Validate, build, and optimize Jaquel queries for ASAM ODS
- 🔌 Built-in ODS connection management (no manual model injection)
- 🧰 29+ MCP tools: schema inspection, query validation, optimization, debugging, and direct ODS query execution
- 📦 Bulk timeseries/submatrix data access and script generation
- 📊 **NEW**: Automatic Jupyter notebook generation for measurement comparison
- 📈 **NEW**: Matplotlib visualization code generation
- 📉 **NEW**: Statistical measurement comparison and correlation analysis
- 🔎 **NEW**: Measurement hierarchy exploration and discovery
- 🏗️ **NEW**: Entity hierarchy visualization (AoTest → AoMeasurement)
- 🤖 **NEW**: AI-guided bulk API learning with `get_bulk_api_help` tool
- 📝 Comprehensive examples, documentation, and test suite

---

## Quick Start

### Clone

```bash
git clone https://github.com/totonga/odsbox-jaquel-mcp.git
cd odsbox-jaquel-mcp
```

### Install Requirements

```bash
python -m venv .venv
.venv/bin/activate
pip install .
```

### Running the Server

```bash
python -m odsbox_jaquel_mcp
```

The server will start on stdio and await MCP protocol messages.

### Testing

See examples:
```bash
python examples/usage_examples.py
python examples/use_mcp_server.py
```

Run tests:
```bash
python run_tests.py
# or
pytest tests/
```

### Building the Package

```bash
python -m build
```

install whl package

```bash
pip install dist/odsbox_jaquel_mcp-0.1.0-py3-none-any.whl
```

## Documentation

- **Tool Reference:** See [`TOOLS_GUIDE.md`](TOOLS_GUIDE.md)
- **API & Usage:** See [`examples/`](examples/) and docstrings
- **Bulk API Learning:** See [`00_START_HERE.md`](00_START_HERE.md) and [`BULK_API_README.md`](BULK_API_README.md)
  - Learn how to efficiently load timeseries data with AI guidance
  - Use `get_bulk_api_help` tool for contextual guidance
  - Find examples and patterns in [`BULK_API_EXAMPLES.md`](BULK_API_EXAMPLES.md)
  - Quick reference: [`BULK_API_QUICK_REF.md`](BULK_API_QUICK_REF.md)
- **Development:**
  - Run: `python -m odsbox_mcp_server.server`
  - Test: `python run_tests.py` or `pytest tests/`
  - Lint: `black .` and `flake8 .`

## Contributing

Pull requests and issues are welcome! Please:
- Follow PEP8 and use type hints
- Add/maintain tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Links

- [ASAM ODS](https://www.asam.net/standards/detail/ods/)
- [MCP Protocol](https://github.com/anthropics/mcp)
- [odsbox](https://pypi.org/project/odsbox/)


## Features

### Core Validation Tools

#### Query Building & Validation
- **validate_jaquel_query** - Check query syntax and structure
- **validate_filter_condition** - Validate filter conditions
- **build_filter_condition** - Construct filter conditions
- **explain_jaquel_query** - Get plain English explanation

#### Pattern & Example Library
- **get_query_pattern** - Get template for common patterns
- **list_query_patterns** - List available patterns
- **generate_query_skeleton** - Generate query skeleton for entity
- **get_operator_documentation** - Learn about operators

#### Query Optimization
- **suggest_optimizations** - Get optimization suggestions
- **merge_filter_conditions** - Combine multiple conditions

#### Debugging Tools
- **debug_query_steps** - Break query into logical steps
- **suggest_error_fixes** - Get suggestions for errors

#### Schema Inspection (Requires Connection)
- **check_entity_schema** - Get all fields for entity
- **validate_field_exists** - Check if field exists
- **validate_filter_against_schema** - Validate against schema
- **list_ods_entities** - List all entities with relationships
- **get_test_to_measurement_hierarchy** - Get ASAM ODS test hierarchy structure

#### Connection Management (NEW)
- **connect_ods_server** - Establish ODS connection
- **disconnect_ods_server** - Close ODS connection
- **get_ods_connection_info** - Get connection status
- **execute_ods_query** - Execute query on ODS server
- **get_submatrix_measurement_quantities** - List measurement quantities for submatrix
- **read_submatrix_data** - Read timeseries data from submatrix
- **generate_submatrix_fetcher_script** - Generate Python scripts for data fetching


## Error Handling

### Common Errors and Solutions

#### Not connected
```json
{
  "error": "Model not loaded",
  "hint": "Connect to ODS server using 'connect_ods_server' tool first"
}
```
Solution: Call connect_ods_server first

#### Invalid entity
```json
{
  "error": "Entity not found: InvalidEntity",
  "available_entities": ["AoUnit", "AoMeasurement", ...]
}
```
Solution: Use valid entity from available_entities

#### Invalid field
```json
{
  "valid": false,
  "issues": ["Field 'invalid_field' not found"],
  "suggestions": ["id", "name", "description"]
}
```
Solution: Use one of the suggested fields

#### Connection failed
```json
{
  "success": false,
  "error": "Connection refused",
  "error_type": "ConnectionError"
}
```
Solution: Check URL, server availability, firewall

## Measurement Analysis & Query Discovery (NEW)

### Understanding ASAM ODS Entity Hierarchy

The `get_test_to_measurement_hierarchy` tool helps you understand the structure of ASAM ODS data:

```python
from odsbox_jaquel_mcp import SchemaInspector

# Get the main ASAM ODS hierarchy
hierarchy = SchemaInspector.get_test_to_measurement_hierarchy()

# Returns:
# {
#   "success": true,
#   "hierarchy_chain": [
#     {
#       "name": "Test",
#       "base_name": "AoTest",
#       "description": "Root of test hierarchy..."
#     },
#     {
#       "name": "SubTest", 
#       "base_name": "AoSubTest",
#       "description": "Intermediate test level..."
#     },
#     {
#       "name": "Measurement",
#       "base_name": "AoMeasurement",
#       "description": "Individual measurement/test case..."
#     }
#   ],
#   "depth": 3
# }
```

**Key Benefits**:
- Understand the data navigation path
- Build correct Jaquel queries following entity relationships
- LLM-friendly output for AI guidance
- Discover "children" relation structure automatically

**Use in Query Building**:
```python
# After understanding hierarchy, build queries like:
query = {
    "AoTest": {
        "name": "MyProject1",
        "children": {
            "name": "SubTest1",
            "children": {
                "name": "MyMeas1"
            }
        }
    }
}
```

### Compare Measurements Statistically

Compare measurements across quantities with correlation and statistics:

```python
from odsbox_jaquel_mcp import MeasurementAnalyzer

result = MeasurementAnalyzer.compare_multiple_measurements(
    quantity_name="Motor_speed",
    measurement_data={
        1: [50, 55, 52, 51, 54],
        2: [52, 56, 53, 52, 55],
        3: [48, 50, 49, 51, 47]
    }
)

# Returns:
# - Individual statistics per measurement (mean, median, stdev)
# - Pairwise comparisons between measurements
# - Correlation coefficients
# - Significance indicators
```

### Query Measurement Hierarchy

Explore and discover measurements in the ODS:

```python
from odsbox_jaquel_mcp import MeasurementHierarchyExplorer

# Extract measurements from ODS query result
measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
    query_result
)

# Get unique tests and quantities
tests = MeasurementHierarchyExplorer.get_unique_tests(measurements)
quantities = MeasurementHierarchyExplorer.get_unique_quantities(measurements)

# Build hierarchy structure
hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
    measurements
)

# Create index for fast lookup
index = MeasurementHierarchyExplorer.build_measurement_index(
    measurements
)
```

**Use Cases**:
- Discover available measurements and quantities
- Find measurements by test type
- Compare performance across test runs
- Analyze consistency and correlations
- Generate analysis notebooks automatically

## Notebook Generation & Visualization (NEW)

### Generate Measurement Comparison Notebooks

The server can automatically generate Jupyter notebooks for analyzing and comparing measurements:

```python
from odsbox_jaquel_mcp import NotebookGenerator

notebook = NotebookGenerator.generate_measurement_comparison_notebook(
    measurement_query_conditions={
        "Name": {"$like": "Profile_*"},
        "TestStep.Test.Name": {"$in": ["Campaign_03"]},
    },
    measurement_quantity_names=["Motor_speed", "Torque"],
    ods_url="https://ods.example.com/api",
    ods_username="user",
    ods_password="password",
    available_quantities=["Motor_speed", "Torque", "Temperature"],
    plot_type="scatter",
    title="Motor Performance Analysis",
    output_path="analysis.ipynb"
)
```

Generated notebooks include:
- Query definition cells
- Automatic data retrieval code
- Data preparation with unit extraction
- Visualization code (scatter, line, or subplots)
- Full documentation and metadata

### Generate Visualization Code

```python
from odsbox_jaquel_mcp import VisualizationTemplateGenerator

code = VisualizationTemplateGenerator.generate_scatter_plot_code(
    measurement_quantity_names=["Speed", "Torque"],
    submatrices_count=6
)
```

Supported plot types:
- **Scatter**: 2D plots with color mapping by independent column
- **Line**: Time series plots with multiple quantities
- **Subplots**: Separate subplots per quantity

### Data Preparation Tools

```python
from odsbox_jaquel_mcp import MeasurementMetadataExtractor

# Extract units and format labels
unit_lookup = MeasurementMetadataExtractor.extract_unit_lookup(columns_df)
labels = MeasurementMetadataExtractor.build_label_dict(columns_df, unit_lookup)

# Generate descriptive titles
titles = MeasurementMetadataExtractor.build_submatrix_title_lookup(
    submatrices_df, measurements_df
)
```

See [`README_EXTENSIONS.md`](README_EXTENSIONS.md) for complete documentation.

## Troubleshooting

### Issue: Tools not discovered
- Ensure mcp>=0.1.0 is installed
- Check ToolsCapability is set in ServerCapabilities
- Restart MCP client

### Issue: Schema tools fail
- Ensure ODS server is accessible
- Check username/password
- Verify network connectivity
- Review server logs

### Issue: Queries timeout
- Increase request_timeout in connect
- Optimize query with suggest_optimizations
- Reduce $rowlimit
- Check ODS server performance

## Performance Tips

1. **Use specific filters** - Avoid querying all records
2. **Limit rows** - Always use `$rowlimit` appropriately
3. **Select attributes** - Only retrieve needed columns
4. **Index awareness** - Filter on indexed fields first
5. **Connection reuse** - Keep connection open when possible
6. **Cache schemas** - Schema inspection is cached

## Security Notes

- Credentials are only held in memory during connection
- Connection is cleaned up on disconnect
- No credentials stored in config files
- Use HTTPS with `verify_certificate: true` for production
- Use strong credentials (not default "sa"/"sa")

## License

This MCP server is provided as-is for ASAM ODS integration.

## Support

For issues or questions:
1. Check the error message and hints
2. Review the documentation and examples
