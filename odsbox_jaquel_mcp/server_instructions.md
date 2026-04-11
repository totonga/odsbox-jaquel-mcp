# ASAM ODS Jaquel MCP Server

Helps an AI agent query and analyze ASAM ODS measurement data via Jaquel queries.

## Mandatory precondition

Most tools require an active ODS connection. Always establish one first:
- Use `ods_connect` (explicit credentials) or `ods_connect_using_env` (env-configured).
- Connection is a singleton and persists across tool calls in the session.
- Call `ods_disconnect` when done.

## Tool selection guide

| Intent | Tool |
|---|---|
| Connect with credentials | `ods_connect` |
| Connect from environment / CI | `ods_connect_using_env` |
| List all entity types | `schema_list_entities` |
| Inspect fields of one entity | `schema_get_entity` |
| Understand test→measurement hierarchy | `schema_test_to_measurement_hierarchy` |
| Check a query before running it | `query_validate` or `query_describe` |
| Look up an operator | `query_get_operator_docs` |
| Get a query template | `query_get_pattern` or `query_generate_skeleton` |
| Run a Jaquel query | `query_execute` |
| List quantities in a submatrix | `data_get_quantities` |
| Read timeseries / bulk data | `data_read_submatrix` |
| Generate a Python fetcher script | `data_generate_fetcher_script` |
| Generate a Jupyter notebook | `plot_comparison_notebook` |
| Generate matplotlib code | `plot_generate_code` |
| Learn the Bulk API | `help_bulk_api` |

## Typical workflows

**Query workflow**: `ods_connect` → `schema_list_entities` → `query_validate` → `query_execute`

**Timeseries workflow**: `ods_connect` → `data_get_quantities` → `data_read_submatrix`

**Analysis workflow**: `query_execute` → `data_get_quantities` → `data_read_submatrix` → `plot_comparison_notebook`

## Key behaviour notes

- `data_read_submatrix` supports wildcard column patterns (`"Temp*"`, `"*Speed"`); prefer it over `query_execute` for large timeseries.
- `ods_connect_using_env` supports auth modes `basic` (default), `m2m`, and `oidc` via `{PREFIX}_MODE`.
- Use starting prompts (`connect_ods_server`, `timeseries_access`, etc.) to guide users through multi-step workflows.

## Reference resources

The server exposes these readable reference documents. Suggest them when relevant:

| Resource URI | When to suggest |
|---|---|
| `file:///odsbox/ods-connection-guide` | User is setting up a connection for the first time |
| `file:///odsbox/ods-entity-hierarchy` | User is unfamiliar with the AoTest → AoSubMatrix hierarchy |
| `file:///odsbox/ods-workflow-reference` | User asks "what are typical workflows?" |
| `file:///odsbox/jaquel-syntax-guide` | User is learning Jaquel query syntax |
| `file:///odsbox/query-operators-reference` | User needs an operator they can't find via `query_get_operator_docs` |
| `file:///odsbox/query-execution-patterns` | User wants ready-made query patterns |
| `file:///odsbox/connection-troubleshooting` | User hits a connection error |
