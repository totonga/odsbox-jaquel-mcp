# ASAM ODS Jaquel MCP Server

This MCP server helps you work with ASAM ODS data using odsbox Jaquel queries.

## 🚀 QUICK START - Choose Your Path

**Path 1: Connect to ODS & Execute Queries**
- `ods_connect` → `schema_list_entities` → `schema_test_to_measurement_hierarchy` → `query_execute`
- Or: `data_read_submatrix` for efficient timeseries access
- Generate reusable scripts: `data_generate_fetcher_script`

**Path 2: Analysis & Visualization**
- Execute queries to get data
- `data_compare_measurements` for statistical analysis
- `plot_comparison_notebook` for Jupyter notebooks
- `plot_generate_code` for matplotlib visualizations

## 📚 TOOL CATEGORIES

**Validation & Debugging**
- Check queries: `query_validate`, `query_describe`
- Check operators: `query_get_operator_docs`

**Query Building**
- Skeletons: `query_generate_skeleton`
- Patterns: `query_list_patterns`, `query_get_pattern`

**Schema & Entity Inspection**
- List entities: `schema_list_entities`, `schema_test_to_measurement_hierarchy`
- Check fields: `schema_get_entity`, `schema_field_exists`

**ODS Connection**
- Manage: `ods_connect`, `ods_disconnect`, `ods_get_connection_info`

**Data Access**
- Submatrix: `data_read_submatrix`, `data_get_quantities`
- Scripts: `data_generate_fetcher_script`

**Analysis & Visualization**
- Compare: `data_compare_measurements`, `data_query_hierarchy`
- Notebooks: `plot_comparison_notebook`
- Plots: `plot_generate_code`

**Help & Documentation**
- `help_bulk_api` - Comprehensive Bulk API guidance

## 💡 COMMON WORKFLOWS

**Workflow 1: Connect to ODS & Execute Query**
1. `ods_connect` - Provide URL, username, password
2. `schema_list_entities` - See available entities
3. `schema_test_to_measurement_hierarchy` - Explore test to measurement structure
4. `schema_get_entity` - Inspect entity fields
5. `query_execute` - Run your query
6. Analyze results with measurement tools

**Workflow 2: Read Timeseries Data Efficiently**
1. `data_get_quantities` - See available data
2. `data_read_submatrix` - Fetch with pattern matching
3. `data_generate_fetcher_script` - Create reusable Python script
4. Use script for automation

**Workflow 3: Compare Multiple Measurements**
1. Execute query to get measurements
2. `data_query_hierarchy` - Explore structure (extract_measurements, get_unique_quantities)
3. `plot_comparison_notebook` - Create Jupyter notebook
4. `data_compare_measurements` - Statistical analysis
5. `plot_generate_code` - Matplotlib code for custom plots

## ⚠️ KEY TIPS

- **Connection State**: Connection persists across tool calls. Call `ods_disconnect` when done.
- **Bulk API**: For large timeseries data (submatrices), prefer `data_read_submatrix` over `query_execute`
- **Pattern Matching**: `data_read_submatrix` supports wildcards for efficient data filtering (e.g., "Temp*", "*Speed")

## ❓ WHEN TO USE WHICH TOOL

**"How do I...?"**
- "...start building a query?" → `query_list_patterns`
- "...validate query?" → `query_describe`
- "...connect to ODS?" → `ods_connect`
- "...connect to ASAM ODS?" → `ods_connect`
- "...find entities?" → `schema_list_entities`
- "...understand structure?" → `schema_test_to_measurement_hierarchy` or `schema_get_entity`
- "...read measurement data?" → `data_read_submatrix` or `query_execute`
- "...create a reusable script?" → `data_generate_fetcher_script`
- "...compare measurements?" → `data_compare_measurements` + `plot_comparison_notebook`
- "...understand submatrix data access?" → `help_bulk_api`

## 📖 INTERACTIVE STARTING PROMPTS

Use these for guided workflows:
- `connect_ods_server` - Learn connection management
- `query_validate` - Validate queries step-by-step
- `explore_patterns` - Discover query patterns
- `timeseries_access` - Learn Bulk API 3-step workflow
- `analyze_measurements` - Statistical analysis & visualization

## 🔗 DOCUMENTATION & EXAMPLES

- **Tool Guide**: https://github.com/totonga/odsbox-jaquel-mcp/blob/main/TOOLS_GUIDE.md
- **Prompts Guide**: https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md
- **Full README**: https://github.com/totonga/odsbox-jaquel-mcp

**Pro Tip**: Always review tool descriptions and examples to understand input/output formats!
