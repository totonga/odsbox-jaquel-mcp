# Common ODS Workflows

## Workflow 1: Connect and Explore Server

**Goal**: Understand what data is available on an ODS server

1. `ods_connect` - Connect with credentials
2. `ods_get_connection_info` - Verify connection
3. `schema_list_entities` - See all available entity types
4. `schema_test_to_measurement_hierarchy` - Understand entity relationships
5. `schema_get_entity` - Inspect fields of a specific entity

**Output**: You now understand the server's data structure

## Workflow 2: Query and Execute

**Goal**: Extract data from ODS server

1. `query_list_patterns` - See available query templates
2. `query_get_pattern` - Get specific pattern
3. `query_describe` - Understand query syntax
4. `query_validate` - Check query syntax
6. `query_execute` - Run query and get results

**Output**: Query results containing measurements and metadata

## Workflow 3: Read Timeseries Data

**Goal**: Access large measurement datasets efficiently

1. `query_execute` - Get measurements with submatrix IDs
2. `data_get_quantities` - See available time series
3. `data_read_submatrix` - Fetch data with optional pattern matching
4. `data_generate_fetcher_script` - Create reusable Python script

**Output**: Timeseries data in desired format (CSV, JSON, etc.)

## Workflow 4: Analyze and Compare

**Goal**: Compare measurements across different runs/conditions

1. `query_execute` - Get measurements
2. `data_query_hierarchy` - Explore measurement structure
   - extract_measurements: Get all measurements
   - get_unique_quantities: See available quantities
   - get_unique_tests: See all test types
3. `data_compare_measurements` - Statistical analysis
4. `plot_comparison_notebook` - Create Jupyter notebook

**Output**: Analysis report with statistics and visualizations

## Workflow 5: Generate Data Access Scripts

**Goal**: Create reusable Python scripts for automation

1. `data_read_submatrix` - Test data access
2. `data_generate_fetcher_script` - Generate production script
3. Choose script type:
   - `basic`: Simple data fetching
   - `advanced`: With analysis and visualization
   - `batch`: For multiple submatrices
   - `analysis`: Statistical analysis included

**Output**: Python script ready for deployment
