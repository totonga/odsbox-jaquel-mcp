# Starting Prompts for ASAM ODS Jaquel MCP Server

Your MCP server now includes **7 helpful starting prompts** that guide users on how to effectively use the available tools. These prompts are designed to help both new and experienced users understand the capabilities and workflows.

## Available Prompts

### 1. 📌 Set Up ODS Server Connection
**Name:** `setup_ods_connection`

Learn how to establish a connection to an ASAM ODS server for live model inspection, schema validation, and direct query execution.

**Related Tools:**
- `connect_ods_server` - Establish connection
- `disconnect_ods_server` - Close connection
- `get_ods_connection_info` - Check status
- `get_test_to_measurement_hierarchy` - Explore hierarchy
- `list_ods_entities` - List entities in model
- `generate_query_skeleton` - Generate entity-specific starters
- `execute_ods_query` - Run queries on server

---

### 2. 📌 Validate a Jaquel Query
**Name:** `validate_query`

Learn how to validate a Jaquel query for syntax errors and best practices. Provides detailed feedback on query structure and suggestions for improvement.

**Related Tools:**
- `validate_jaquel_query` - Validate entire queries
- `validate_field_exists` - Check if fields exist

---

### 3. 📌 Explore Jaquel Query Patterns
**Name:** `explore_patterns`

Discover common Jaquel query patterns and templates for:
- Getting all instances
- Filtering by ID or name
- Case-insensitive search
- Time range queries
- Joins (inner/outer)
- Aggregations

**Related Tools:**
- `list_query_patterns` - See all patterns
- `get_query_pattern` - Get specific pattern
- `generate_query_skeleton` - Generate entity-specific starters

---

### 5. 📌 Bulk Data Access & Submatrix Reading
**Name:** `bulk_data_access`

Master the **3-step Bulk API workflow** for efficient timeseries data access:
1. **Locate** - Find the submatrix ID
2. **Access** - Use Bulk API to read data
3. **Process** - Transform and analyze

**Related Tools:**
- `read_submatrix_data` - Read data with pattern matching
- `get_submatrix_measurement_quantities` - List available quantities
- `generate_submatrix_fetcher_script` - Generate reusable scripts
- `get_bulk_api_help` - Detailed guidance

**Script Types Available:**
- `basic` - Simple data fetching
- `advanced` - With analysis and visualization
- `batch` - For processing multiple submatrices
- `analysis` - Statistical analysis included

---

### 6. 📌 Measurement Analysis & Comparison
**Name:** `analyze_measurements`

Learn how to analyze and compare measurements across quantities with:
- Statistical analysis
- Jupyter notebook generation
- Matplotlib visualization code
- Measurement hierarchy exploration

**Related Tools:**
- `compare_measurements` - Statistical comparison
- `query_measurement_hierarchy` - Explore structure
- `generate_measurement_comparison_notebook` - Create notebooks
- `generate_plotting_code` - Generate visualization code

**Hierarchy Operations:**
- `extract_measurements` - Get from query results
- `build_hierarchy` - Create hierarchical structure
- `get_unique_tests` - Find test names
- `get_unique_quantities` - List quantities
- `build_index` - Create searchable index

---

### 7. 📌 Optimize & Debug Jaquel Queries
**Name:** `optimize_query`

Learn how to optimize queries for better performance and readability:
- Query simplification suggestions
- Step-by-step debugging
- Error fix recommendations

**Related Tools:**
- `suggest_optimizations` - Get simplifications
- `debug_query_steps` - Step-by-step breakdown
- `suggest_error_fixes` - Fix recommendations
- `explain_query` - Understand behavior

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
content = PromptLibrary.get_prompt_content("validate_query", {})

# Get prompt with arguments
content = PromptLibrary.get_prompt_content(
    "bulk_data_access",
    {"use_case": "batch processing"}
)
```

---

## Prompt Features

### Dynamic Content
Prompts can include optional arguments to customize their content:

```json
{
  "name": "validate_query",
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

Enjoy using your enhanced ASAM ODS Jaquel MCP server! 🚀
