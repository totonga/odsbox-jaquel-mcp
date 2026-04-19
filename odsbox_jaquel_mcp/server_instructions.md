# ASAM ODS Jaquel MCP Server

Query and analyze ASAM ODS measurement data via Jaquel queries.

## Core rules

1. **Inspect first.** Always query the live server with MCP tools before generating any code. Use schemas, queries, and data-reader tools to answer the user directly.
2. **Scripts and notebooks on demand only.** Generate standalone Python scripts or Jupyter notebooks only when the user explicitly requests them or when MCP tools cannot fulfil the need.
3. **Connect first.** Most tools require an active connection — use `ods_connect` or `ods_connect_using_env`. Connection is a singleton; call `ods_disconnect` when done.

## Typical workflows

**Query**: `ods_connect` → `schema_list_entities` → `query_validate` → `query_execute`
**Timeseries**: `ods_connect` → `data_get_quantities` → `data_read_submatrix`
**Analysis**: `query_execute` → `data_get_quantities` → `data_read_submatrix` → `plot_comparison_notebook`

## Notes

- When generating any Python script, use `uv` as the package manager and `odsbox[oidc]` as the dependency (covers all auth modes).
- `data_read_submatrix` supports wildcard patterns (`"Temp*"`, `"*Speed"`); prefer over `query_execute` for large timeseries.
- `ods_connect_using_env` auth modes: `basic` (default), `m2m`, `oidc` — set via `{PREFIX}_MODE`.
- Use starting prompts (`connect_ods_server`, `timeseries_access`, …) to guide multi-step workflows.

## Reference resources

| Resource URI | When to suggest |
|---|---|
| `file:///odsbox/ods-connection-guide` | Setting up a connection for the first time |
| `file:///odsbox/ods-entity-hierarchy` | Unfamiliar with AoTest → AoSubMatrix hierarchy |
| `file:///odsbox/ods-workflow-reference` | "What are typical workflows?" |
| `file:///odsbox/jaquel-syntax-guide` | Learning Jaquel query syntax |
| `file:///odsbox/query-operators-reference` | Operator not found via `query_get_operator_docs` |
| `file:///odsbox/query-execution-patterns` | Ready-made query patterns |
| `file:///odsbox/connection-troubleshooting` | Connection error |
