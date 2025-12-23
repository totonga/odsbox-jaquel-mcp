"""Bulk API help and guidance for AI assistants.

This module provides integrated help content to guide AI models on how to
correctly use the bulk API for loading timeseries data from ASAM ODS.
"""

from __future__ import annotations


class BulkAPIGuide:
    """Centralized guide for bulk API usage in MCP server context."""

    # The fundamental rule that MUST be followed
    THE_3_STEP_RULE = """
╔════════════════════════════════════════════════════════════════════════╗
║                        THE 3-STEP RULE (MANDATORY)                     ║
║                                                                        ║
║  Every interaction with bulk API MUST follow these steps IN ORDER:     ║
║                                                                        ║
║  1️⃣  CONNECT: connect_ods_server(url, username, password)             ║
║      └─ Establish connection to ODS server                             ║
║                                                                        ║
║  2️⃣  DISCOVER: get_submatrix_measurement_quantities(submatrix_id)     ║
║      └─ Find what measurement columns are available                    ║
║                                                                        ║
║  3️⃣  LOAD: read_submatrix_data(submatrix_id, patterns, ...)           ║
║      └─ Load the actual timeseries data                                ║
║                                                                        ║
║  NO EXCEPTIONS. ALWAYS ALL 3 STEPS. ALWAYS IN THIS ORDER.              ║
╚════════════════════════════════════════════════════════════════════════╝
    """

    # Quick reference
    QUICK_START = """
QUICK START: Loading Timeseries Data

📋 Workflow:
  1. connect_ods_server(url, user, pass)
  2. get_submatrix_measurement_quantities(submatrix_id)
  3. read_submatrix_data(submatrix_id, patterns=[...])

📊 What to do next:
  • Export to CSV/JSON/Parquet: generate_submatrix_fetcher_script
  • Compare multiple submatrices: generate_measurement_comparison_notebook
  • Analyze data: generate_submatrix_fetcher_script with include_analysis

⚠️  Common mistake: Using Jaquel queries to load data
    → Use bulk API instead (read_submatrix_data)
    → Jaquel is for metadata, bulk API is for data values
    """

    # When to use bulk vs Jaquel
    BULK_VS_JAQUEL = """
BULK API vs JAQUEL QUERIES

┌─────────────────────────────────────────────────────────────┐
│ USE BULK API WHEN:                                          │
├─────────────────────────────────────────────────────────────┤
│ • Loading actual measurement/timeseries data                │
│ • Need rows and columns of numbers                          │
│ • Performing analysis, plotting, or statistics              │
│ • Exporting data to files (CSV, JSON, etc.)                 │
│                                                             │
│ TOOLS: read_submatrix_data, generate_*_fetcher_script       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ USE JAQUEL QUERIES WHEN:                                    │
├─────────────────────────────────────────────────────────────┤
│ • Exploring data model structure                            │
│ • Finding entities and relationships                        │
│ • Searching for measurement definitions                     │
│ • Checking what data exists                                 │
│                                                             │
│ TOOLS: execute_ods_query, validate_query             │
└─────────────────────────────────────────────────────────────┘

KEY DIFFERENCE:
  Bulk API:   "Give me the numbers" (data)
  Jaquel:     "Tell me about the structure" (metadata)
    """

    # Pattern syntax
    PATTERN_SYNTAX = """
COLUMN PATTERN SYNTAX

Use measurement_quantity_patterns to filter which columns to load:

  Exact Match:      ["Temperature"]
                    └─ Loads only "Temperature"

  Start Wildcard:   ["Temp*"]
                    └─ Matches: Temperature, Temp_avg, Temp_max

  End Wildcard:     ["*Speed"]
                    └─ Matches: Engine_Speed, Wheel_Speed

  Contains:         ["*Temp*"]
                    └─ Matches: Engine_Temp, Coolant_Temp, TempOffset

  Multiple:         ["Time", "Temp*", "Pressure"]
                    └─ Load Time + all Temp columns + Pressure

  All columns:      []
                    └─ Load everything (use carefully!)

  Case-insensitive: set case_insensitive: true
                    └─ "*temp*" matches Temperature, TEMPERATURE, etc.
    """

    # Decision tree for AI
    DECISION_TREE = """
DECISION TREE: What Should I Do?

User asks about data-related action:
  │
  ├─ "What data exists?" / "Show measurements" / "What columns?"
  │  └─> Use: get_submatrix_measurement_quantities
  │      └─> Shows available columns with units and types
  │
  ├─ "Load the data" / "Show me values" / "Get measurements"
  │  ├─> Connect: connect_ods_server (if needed)
  │  ├─> Discover: get_submatrix_measurement_quantities
  │  └─> Load: read_submatrix_data
  │
  ├─ "Compare these measurements across runs"
  │  └─> Use: generate_measurement_comparison_notebook
  │      └─> Creates Jupyter notebook with plots & analysis
  │
  ├─ "Generate a script I can reuse"
  │  ├─> First understand: get_submatrix_measurement_quantities
  │  └─> Then: generate_submatrix_fetcher_script (basic/advanced/batch/analysis)
  │
  ├─ "Plot this data" / "Analyze it"
  │  ├─> Load: read_submatrix_data
  │  └─> Generate: generate_submatrix_fetcher_script with include_visualization
  │
  └─ "Help me find data" / "Which submatrix has...?"
     └─> Use: JAQUEL QUERIES (not bulk API)
         └─> execute_ods_query to explore metadata
    """

    # Common mistakes
    COMMON_MISTAKES = """
TOP 5 AI MISTAKES WITH BULK API

❌ MISTAKE 1: Using Jaquel to Load Data
   Example: execute_ods_query to get measurement values
   Problem: Jaquel queries return metadata, not data
   Fix: Use read_submatrix_data instead

❌ MISTAKE 2: Skipping Discovery
   Example: Call read_submatrix_data without first checking available columns
   Problem: Don't know exact column names or if columns exist
   Fix: Call get_submatrix_measurement_quantities first

❌ MISTAKE 3: Forgetting to Connect
   Example: Call read_submatrix_data without connect_ods_server
   Problem: Error - "Not connected to ODS server"
   Fix: Always call connect_ods_server FIRST

❌ MISTAKE 4: Assuming Column Names
   Example: Use pattern "temp" without checking if "Temperature" exists
   Problem: Pattern won't match if casing or name is different
   Fix: Use discovery results + case_insensitive: true + wildcards

❌ MISTAKE 5: Loading All Columns Always
   Example: measurement_quantity_patterns: [] (load everything)
   Problem: Very slow for large submatrices, high memory
   Fix: Specify exact columns: ["Time", "Temperature", "Pressure"]
    """

    # Step-by-step guide
    STEP_BY_STEP = """
STEP-BY-STEP GUIDE: Load Temperature Data from Submatrix 123

STEP 1: CONNECT
  Tool: connect_ods_server
  Args: {
    "url": "http://localhost:8087/api",
    "username": "your_user",
    "password": "your_pass"
  }
  Result: Connection established ✅

STEP 2: DISCOVER
  Tool: get_submatrix_measurement_quantities
  Args: { "submatrix_id": 123 }
  Result: List of available columns:
    - Time (independent, seconds)
    - Engine_Temperature (°C)
    - Engine_Speed (rpm)
    - Fuel_Pressure (bar)

STEP 3: LOAD
  Tool: read_submatrix_data
  Args: {
    "submatrix_id": 123,
    "measurement_quantity_patterns": ["Time", "Engine_Temperature"],
    "date_as_timestamp": true,
    "set_independent_as_index": true
  }
  Result: DataFrame with 5000 rows, 2 columns ✅

OPTIONAL: GENERATE SCRIPT
  Tool: generate_submatrix_fetcher_script
  Args: {
    "submatrix_id": 123,
    "script_type": "basic",
    "measurement_quantity_patterns": ["Time", "Engine_Temperature"],
    "output_format": "csv"
  }
  Result: Python script for reuse ✅

DONE! 🎉
    """

    # Response templates
    RESPONSE_TEMPLATE = """
TEMPLATE: How to Respond to Data Requests

When user says: "Load the data from submatrix 123"

Step 1: PREPARE
  "Let me help you load that data. I'll follow the proper workflow..."

Step 2: CONNECT
  "First, connecting to the ODS server..."
  [Call connect_ods_server if needed]

Step 3: DISCOVER
  "Now I'll check what measurement columns are available..."
  [Call get_submatrix_measurement_quantities]
  Show: "I found 4 columns: Time, Temperature, Pressure, Humidity"

Step 4: CONFIRM
  "Which columns would you like me to load?"
  [Offer options or make recommendations]

Step 5: LOAD
  "Loading your data..."
  [Call read_submatrix_data]

Step 6: DELIVER
  "✅ Loaded 5000 rows with 3 columns"
  "Preview: [show first few rows]"

Step 7: OFFER
  "What would you like to do next?"
  - Export to CSV/JSON/Excel?
  - Plot it?
  - Compare with other data?
  - Generate a reusable script?
    """

    # Troubleshooting
    TROUBLESHOOTING = """
TROUBLESHOOTING BULK API ERRORS

ERROR: "Not connected to ODS server"
  Cause: connect_ods_server not called
  Fix: Call connect_ods_server(url, user, pass) first
  
ERROR: "No columns matched the pattern"
  Cause: Column names don't match pattern
  Fix: 
    1. Call get_submatrix_measurement_quantities to see exact names
    2. Use exact names or correct wildcards
    3. Try case_insensitive: true

ERROR: "Submatrix not found" or invalid ID
  Cause: submatrix_id doesn't exist
  Fix: Use Jaquel query to find valid IDs:
    execute_ods_query({
      "AoSubmatrix": {},
      "$attributes": ["id", "name"]
    })

ERROR: Data loading is very slow
  Cause: Loading too many columns or very large submatrix
  Fix:
    1. Load specific columns only (not all)
    2. Use column patterns to filter
    3. Generate script for batch processing
    4. Use parquet format for export

ERROR: Memory error when loading
  Cause: Submatrix is too large
  Fix:
    1. Filter to specific columns
    2. Generate batch fetcher script
    3. Process in chunks
    4. Use parquet format
    """

    # Tool usage patterns
    TOOL_PATTERNS = """
COMMON TOOL USAGE PATTERNS

┌─────────────────────────────────────────────────────────────┐
│ Pattern 1: Simple Load                                      │
├─────────────────────────────────────────────────────────────┤
│ 1. connect_ods_server                                       │
│ 2. get_submatrix_measurement_quantities                     │
│ 3. read_submatrix_data                                      │
│ Result: DataFrame in memory                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Pattern 2: Load + Export                                    │
├─────────────────────────────────────────────────────────────┤
│ 1. connect_ods_server                                       │
│ 2. get_submatrix_measurement_quantities                     │
│ 3. generate_submatrix_fetcher_script (output_format: csv)   │
│ Result: Python script that saves to CSV                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Pattern 3: Multi-Submatrix Comparison                       │
├─────────────────────────────────────────────────────────────┤
│ 1. connect_ods_server                                       │
│ 2. generate_measurement_comparison_notebook                 │
│ Result: Jupyter notebook with plots & analysis              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Pattern 4: Load + Analyze                                   │
├─────────────────────────────────────────────────────────────┤
│ 1. connect_ods_server                                       │
│ 2. get_submatrix_measurement_quantities                     │
│ 3. generate_submatrix_fetcher_script (script_type: analysis)│
│ Result: Python script with plots & statistics               │
└─────────────────────────────────────────────────────────────┘
    """

    @staticmethod
    def get_help(topic: str) -> str:
        """Get help for a specific topic.

        Args:
            topic: Help topic (e.g., "3-step-rule", "bulk-vs-jaquel", "patterns")

        Returns:
            Help text for the topic
        """
        help_topics = {
            "3-step-rule": BulkAPIGuide.THE_3_STEP_RULE,
            "quick-start": BulkAPIGuide.QUICK_START,
            "bulk-vs-jaquel": BulkAPIGuide.BULK_VS_JAQUEL,
            "patterns": BulkAPIGuide.PATTERN_SYNTAX,
            "decision-tree": BulkAPIGuide.DECISION_TREE,
            "mistakes": BulkAPIGuide.COMMON_MISTAKES,
            "step-by-step": BulkAPIGuide.STEP_BY_STEP,
            "response-template": BulkAPIGuide.RESPONSE_TEMPLATE,
            "troubleshooting": BulkAPIGuide.TROUBLESHOOTING,
            "tool-patterns": BulkAPIGuide.TOOL_PATTERNS,
        }

        return help_topics.get(
            topic,
            f"Unknown topic: {topic}\n\nAvailable topics:\n" + "\n".join(f"  - {t}" for t in help_topics.keys()),
        )

    @staticmethod
    def get_all_help() -> str:
        """Get all help content concatenated."""
        return (
            BulkAPIGuide.THE_3_STEP_RULE
            + "\n\n"
            + BulkAPIGuide.QUICK_START
            + "\n\n"
            + BulkAPIGuide.BULK_VS_JAQUEL
            + "\n\n"
            + BulkAPIGuide.PATTERN_SYNTAX
            + "\n\n"
            + BulkAPIGuide.DECISION_TREE
            + "\n\n"
            + BulkAPIGuide.COMMON_MISTAKES
            + "\n\n"
            + BulkAPIGuide.STEP_BY_STEP
            + "\n\n"
            + BulkAPIGuide.TROUBLESHOOTING
            + "\n\n"
            + BulkAPIGuide.TOOL_PATTERNS
        )

    @staticmethod
    def get_contextual_help(current_tool: str) -> str:
        """Get contextual help for a specific tool.

        Args:
            current_tool: Name of the tool (e.g., "read_submatrix_data")

        Returns:
            Contextual help for the tool
        """
        contextual_tips = {
            "connect_ods_server": """
⚠️  IMPORTANT: This must be called FIRST in any bulk API workflow.

Steps:
1. Call this first with URL, username, password
2. All subsequent bulk API calls depend on this connection

Don't forget: If you need to connect, do it BEFORE discovery!
            """,
            "get_submatrix_measurement_quantities": """
📋 This MUST be called before read_submatrix_data.

It shows:
- What columns are available
- Column names (exact casing matters)
- Units and data types
- Which column is "independent" (usually Time)

Always check this first - don't assume column names exist!
            """,
            "read_submatrix_data": """
🎯 This loads the actual data.

Requirements:
- Must call connect_ods_server first
- Must call get_submatrix_measurement_quantities first to know column names
- Use measurement_quantity_patterns to specify which columns

Parameters:
- measurement_quantity_patterns: Use exact names or wildcards from discovery
- case_insensitive: Set true if unsure about casing
- set_independent_as_index: Usually true for time series
            """,
            "generate_submatrix_fetcher_script": """
♻️  This generates a reusable Python script.

Use this when:
- You need to load this data repeatedly
- You want error handling and logging
- You want to automate the process

Script types:
- "basic": Simple loading
- "advanced": Error handling + logging
- "batch": Multiple submatrices
- "analysis": Plots + statistics
            """,
            "generate_measurement_comparison_notebook": """
📊 This creates a Jupyter notebook for comparing multiple submatrices.

Use this when:
- Comparing measurements across multiple test runs
- Need side-by-side plots
- Want statistical analysis

This is more efficient than manually loading multiple submatrices!
            """,
        }

        return contextual_tips.get(
            current_tool,
            f"No specific help for {current_tool}. " "See 'get help bulk-api' for general guidance.",
        )
