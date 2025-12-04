"""Example usage of the Jaquel MCP Server tools."""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from odsbox_jaquel_mcp import JaquelExamples, JaquelOptimizer, JaquelValidator


def example_validate_query():
    """Example: Validate a Jaquel query."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Validate a Jaquel Query")
    print("=" * 70)

    query = {
        "AoMeasurement": {"name": {"$like": "Test*"}, "measurement_begin": {"$between": ["2023-01-01", "2023-12-31"]}},
        "$attributes": {"id": 1, "name": 1, "description": 1},
        "$orderby": {"name": 1},
        "$options": {"$rowlimit": 10},
    }

    print("\nQuery to validate:")
    print(json.dumps(query, indent=2))

    result = JaquelValidator.validate_query(query)
    print("\nValidation Result:")
    print(json.dumps(result, indent=2))


def example_get_patterns():
    """Example: List and get query patterns."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: List Available Query Patterns")
    print("=" * 70)

    patterns = JaquelExamples.list_patterns()
    print("\nAvailable patterns:")
    for pattern in patterns:
        print(f"  - {pattern}")

    print("\nGetting 'case_insensitive_search' pattern:")
    pattern = JaquelExamples.get_pattern("case_insensitive_search")
    print(json.dumps(pattern, indent=2))


def example_generate_skeleton():
    """Example: Generate query skeleton."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Generate Query Skeleton")
    print("=" * 70)

    entity = "AoMeasurement"
    operation = "search_and_select"

    print("\nGenerating skeleton for:")
    print(f"  Entity: {entity}")
    print(f"  Operation: {operation}")

    skeleton = JaquelExamples.generate_query_skeleton(entity, operation)
    print("\nGenerated skeleton:")
    print(json.dumps(skeleton, indent=2))


def example_optimize_query():
    """Example: Suggest query optimizations."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Optimize Query")
    print("=" * 70)

    # Verbose query with optimization opportunities
    verbose_query = {
        "AoUnit": {"id": {"$eq": 123}, "name": {"$like": "Test*", "$options": "i"}},
        "$attributes": {"id": 1, "name": 1},
    }

    print("\nVerbose query:")
    print(json.dumps(verbose_query, indent=2))

    suggestions = JaquelOptimizer.suggest_simplifications(verbose_query)
    print("\nOptimization suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")


def example_operator_docs():
    """Example: Get operator documentation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Operator Documentation")
    print("=" * 70)

    operators = ["$eq", "$like", "$between", "$and", "$distinct"]

    for operator in operators:
        print(f"\n--- Operator: {operator} ---")
        info = JaquelValidator.get_operator_info(operator)
        print(json.dumps(info, indent=2))


def example_build_conditions():
    """Example: Build filter conditions."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Build Filter Conditions")
    print("=" * 70)

    # Example 1: Simple equality
    print("\nCondition 1: Simple equality")
    print("  Field: name, Operator: $eq, Value: 'MyTest'")
    result = JaquelValidator.validate_filter_condition({"name": {"$eq": "MyTest"}})
    print(f"  Valid: {result['valid']}")

    # Example 2: Wildcard search
    print("\nCondition 2: Wildcard search (case-insensitive)")
    print("  Field: name, Operator: $like, Value: 'Test*'")
    result = JaquelValidator.validate_filter_condition({"name": {"$like": "Test*", "$options": "i"}})
    print(f"  Valid: {result['valid']}")

    # Example 3: Range query
    print("\nCondition 3: Range query")
    print("  Field: value, Operator: $between, Value: [0, 100]")
    result = JaquelValidator.validate_filter_condition({"value": {"$between": [0, 100]}})
    print(f"  Valid: {result['valid']}")

    # Example 4: Logical AND
    print("\nCondition 4: Logical AND")
    print("  Multiple conditions combined")
    condition = {"$and": [{"status": "active"}, {"value": {"$gte": 0}}, {"value": {"$lte": 100}}]}
    result = JaquelValidator.validate_filter_condition(condition)
    print(f"  Valid: {result['valid']}")
    print(f"  Condition: {json.dumps(condition, indent=4)}")


def example_common_queries():
    """Example: Show common query patterns."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Common Query Patterns")
    print("=" * 70)

    patterns_to_show = ["get_all_instances", "get_by_id", "time_range", "inner_join", "outer_join", "aggregates"]

    for pattern_name in patterns_to_show:
        print(f"\n--- Pattern: {pattern_name} ---")
        pattern = JaquelExamples.get_pattern(pattern_name)
        print(f"Description: {pattern['description']}")
        print(f"Explanation: {pattern['explanation']}")
        print("\nTemplate:")
        print(pattern["template"])


def example_explain_query():
    """Example: Explain a query in plain English."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Explain Query")
    print("=" * 70)

    from odsbox_jaquel_mcp import _explain_query

    query = {
        "AoMeasurement": {"name": {"$like": "Profile*"}, "measurement_begin": {"$gte": "2023-01-01T00:00:00Z"}},
        "$attributes": {"id": 1, "name": 1, "measurement_begin": 1, "test.name": 1},
        "$orderby": {"measurement_begin": 0},
        "$options": {"$rowlimit": 50, "$rowskip": 10},
    }

    print("\nOriginal Query:")
    print(json.dumps(query, indent=2))

    print("\n\nPlain English Explanation:")
    print(_explain_query(query))


def example_submatrix_tools():
    """Example: Using submatrix data reading tools."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Submatrix Data Reading Tools")
    print("=" * 70)

    print(
        """
These tools require an active ODS server connection.
Use the MCP server tools in the following order:

1. Connect to ODS server:
   Tool: connect_ods_server
   Parameters: {"url": "http://localhost:8087/api", "username": "user", "password": "pass"}

2. Get available measurement quantities for a submatrix:
   Tool: get_submatrix_measurement_quantities
   Parameters: {"submatrix_id": 123}
   
   Returns: List of measurement quantities with names, units, etc.

3. Read timeseries data from the submatrix:
   Tool: read_submatrix_data
   Parameters: {
       "submatrix_id": 123,
       "measurement_quantity_patterns": ["Time", "Temperature*", "Pressure"],
       "case_insensitive": false,
       "date_as_timestamp": true,
       "set_independent_as_index": true
   }
   
   Returns: DataFrame with timeseries data, column names, row count, and preview.

4. Generate a Python script for automated data fetching:
   Tool: generate_submatrix_fetcher_script
   Parameters: {
       "submatrix_id": 123,
       "script_type": "basic",
       "output_format": "csv",
       "include_visualization": false,
       "include_analysis": false
   }
   
   Returns: Complete Python script for fetching data with proper error handling.

5. Disconnect when done:
   Tool: disconnect_ods_server
   Parameters: {}
"""
    )


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("JAQUEL MCP SERVER - USAGE EXAMPLES")
    print("=" * 70)

    example_validate_query()
    example_get_patterns()
    example_generate_skeleton()
    example_optimize_query()
    example_operator_docs()
    example_build_conditions()
    example_common_queries()
    example_explain_query()
    example_submatrix_tools()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
