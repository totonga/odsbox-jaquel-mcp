# Starting Prompts for ASAM ODS Jaquel MCP Server

The MCP server includes **helpful starting prompts** that guide users on how to effectively use the available tools. These prompts are designed to help both new and experienced users understand the capabilities and workflows.

## Available Prompts

### 📌 Set Up ODS Server Connection
**Name:** `connect_ods_server`

Learn how to establish a connection to an ASAM ODS server for live model inspection, schema validation, and direct query execution.

**Related Tools:**
- `ods_connect` - Establish connection
- `ods_disconnect` - Close connection
- `ods_get_connection_info` - Check status
- `schema_test_to_measurement_hierarchy` - Explore hierarchy
- `schema_list_entities` - List entities in model
- `query_generate_skeleton` - Generate entity-specific starters
- `query_execute` - Run queries on server

---

### 📌 Validate a Jaquel Query
**Name:** `query_validate`

Learn how to validate a Jaquel query for syntax errors and best practices. Provides detailed feedback on query structure and suggestions for improvement.

**Related Tools:**
- `query_validate` - Validate entire queries
- `schema_field_exists` - Check if fields exist

---

### 📌 Explore Jaquel Query Patterns
**Name:** `explore_patterns`

Discover common Jaquel query patterns and templates for:
- Getting all instances
- Filtering by ID or name
- Case-insensitive search
- Time range queries
- Joins (inner/outer)
- Aggregations

**Related Tools:**
- `query_list_patterns` - See all patterns
- `query_get_pattern` - Get specific pattern
- `query_generate_skeleton` - Generate entity-specific starters

---

### 📌 Bulk Data Access & Submatrix Reading
**Name:** `timeseries_access`

Master the **3-step Bulk API workflow** for efficient timeseries data access:
1. **Locate** - Find the submatrix ID
2. **Access** - Use Bulk API to read data
3. **Process** - Transform and analyze

**Related Tools:**
- `data_read_submatrix` - Read data with pattern matching
- `data_get_quantities` - List available quantities
- `data_generate_fetcher_script` - Generate reusable scripts
- `help_bulk_api` - Detailed guidance

**Script Types Available:**
- `basic` - Simple data fetching
- `advanced` - With analysis and visualization
- `batch` - For processing multiple submatrices
- `analysis` - Statistical analysis included

---

### 📌 Measurement Analysis & Comparison
**Name:** `analyze_measurements`

Learn how to analyze and compare measurements across quantities with:
- Statistical analysis
- Jupyter notebook generation
- Matplotlib visualization code
- Measurement hierarchy exploration

**Related Tools:**
- `data_compare_measurements` - Statistical comparison
- `data_query_hierarchy` - Explore structure
- `plot_comparison_notebook` - Create notebooks
- `plot_generate_code` - Generate visualization code

**Hierarchy Operations:**
- `extract_measurements` - Get from query results
- `build_hierarchy` - Create hierarchical structure
- `get_unique_tests` - Find test names
- `get_unique_quantities` - List quantities
- `build_index` - Create searchable index

---

## How to Use Starting Prompts

### With Claude (GitHub Copilot)
When using the MCP server with Claude:
1. The prompts appear as "Starting Prompts" in the chat interface
2. Click any prompt to start a guided conversation
3. Optionally provide context (query examples, server details, etc.)
4. Claude will guide you through using the relevant tools

### Programmatic Access
You can also access prompts programmatically:

```python
from odsbox_jaquel_mcp.prompts import PromptLibrary

# Get all prompts
prompts = PromptLibrary.get_all_prompts()

# Get specific prompt content
content = PromptLibrary.get_prompt_content("query_validate", {})

# Get prompt with arguments
content = PromptLibrary.get_prompt_content(
    "timeseries_access",
    {"use_case": "batch processing"}
)
```

---

## Prompt Features

### Dynamic Content
Prompts can include optional arguments to customize their content:

```json
{
  "name": "query_validate",
  "title": "Validate a Jaquel Query",
  "arguments": [
    {
      "name": "query_example",
      "description": "(Optional) A sample Jaquel query to validate",
      "required": false
    }
  ]
}
```

### Rich Formatting
Each prompt includes:
- Clear title and description
- Step-by-step instructions
- List of related tools
- Examples and best practices
- Links to workflows

### Context-Aware
Prompts intelligently reference other tools and workflows, making it easy to discover the full capabilities of the server.

---

## Best Practices

1. **Start with an appropriate prompt** for your task
2. **Provide context** (query examples, use cases) when available
3. **Follow the suggested workflow** in the prompt
4. **Use related tools** that the prompt recommends
5. **Refer back to prompts** if you get stuck

---

## Integration with MCP Clients

The prompts are exposed through the MCP protocol via:
- `list_prompts()` - Lists all available prompts
- `get_prompt(name, arguments)` - Gets specific prompt content

Any MCP client (like Claude in VS Code) can discover and use these prompts automatically.

---

## Adding New Prompts

To add more starting prompts, edit `odsbox_jaquel_mcp/prompts.py`:

1. Add a new static method to the `PromptLibrary` class
2. Return a `Prompt` object with name, title, description, and arguments
3. Add handling in `get_prompt_content()` to generate the content
4. Add it to `get_all_prompts()` return list

Example:
```python
@staticmethod
def _custom_prompt() -> Prompt:
    return Prompt(
        name="custom_workflow",
        title="Custom Workflow Title",
        description="Description of the workflow",
        arguments=[
            PromptArgument(name="param", description="Param description")
        ]
    )

@staticmethod
def get_prompt_content(prompt_name: str, arguments: dict | None = None) -> str:
    # ... existing code ...
    elif prompt_name == "custom_workflow":
        return "# Custom Workflow\n\n..."
```

---

## Summary

Starting prompts provide an **onboarding experience** for your MCP server, helping users:
- Discover available functionality
- Learn best practices
- Get guided assistance
- Avoid common mistakes
- Efficiently accomplish their goals

Enjoy using ASAM ODS Jaquel MCP server! 🚀
