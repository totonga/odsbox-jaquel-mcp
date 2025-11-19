"""
Use the MCP Server tools to build a Jaquel query for getting Projects.

This demonstrates how to use the odsbox_jaquel_mcp tools
to help construct and validate queries.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from odsbox_jaquel_mcp import JaquelExamples, JaquelOptimizer, JaquelValidator


async def main():
    """Demonstrate using MCP server tools for query building."""

    print("=" * 80)
    print("USING MCP SERVER TOOLS TO BUILD PROJECT QUERY")
    print("=" * 80)

    # ========================================================================
    # STEP 1: List available patterns
    # ========================================================================
    print("\nSTEP 1: View available query patterns")
    print("-" * 80)

    patterns = JaquelExamples.list_patterns()
    print(f"Available patterns: {patterns}\n")

    # ========================================================================
    # STEP 2: Get a query skeleton
    # ========================================================================
    print("\nSTEP 2: Generate query skeleton for StructureLevel entity")
    print("-" * 80)

    skeleton = JaquelExamples.generate_query_skeleton(entity_name="StructureLevel", operation="get_all")
    print("Generated skeleton:")
    print(json.dumps(skeleton, indent=2))

    # ========================================================================
    # STEP 3: Build the actual project query
    # ========================================================================
    print("\n\nSTEP 3: Build the Projects query")
    print("-" * 80)

    projects_query = {
        "StructureLevel": {},
        "$attributes": {
            "id": 1,
            "name": 1,
            "description": 1,
            "type": 1,
        },
        "$orderby": {"name": 1},
    }

    print("Query:")
    print(json.dumps(projects_query, indent=2))

    # ========================================================================
    # STEP 4: Validate the query using MCP server
    # ========================================================================
    print("\n\nSTEP 4: Validate query using MCP server")
    print("-" * 80)

    validation_result = JaquelValidator.validate_query(projects_query)
    print("Validation result:")
    print(json.dumps(validation_result, indent=2))

    if validation_result.get("valid"):
        print("\n✓ Query is VALID and ready to use!")
    else:
        print("\n✗ Query has issues:")
        for error in validation_result.get("errors", []):
            print(f"  - {error}")

    # ========================================================================
    # STEP 5: Check for optimization suggestions
    # ========================================================================
    print("\n\nSTEP 5: Get optimization suggestions from MCP server")
    print("-" * 80)

    suggestions = JaquelOptimizer.suggest_simplifications(projects_query)
    print("Optimization suggestions:")
    if suggestions:
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    else:
        print("  (No suggestions)")

    # ========================================================================
    # STEP 6: Build filter conditions using MCP tools
    # ========================================================================
    print("\n\nSTEP 6: Build filter conditions for specific project type")
    print("-" * 80)

    # Example: filter for PROJECT type only
    print("\nBuilding filter: type == 'PROJECT'")

    filter_condition = {"type": {"$eq": "PROJECT"}}

    print("Filter condition:")
    print(json.dumps(filter_condition, indent=2))

    # Validate the filter
    filter_validation = JaquelValidator.validate_filter_condition(filter_condition, field_name="type")
    print("\nFilter validation:")
    print(json.dumps(filter_validation, indent=2))

    # ========================================================================
    # STEP 7: Create filtered query
    # ========================================================================
    print("\n\nSTEP 7: Create filtered query for PROJECT type only")
    print("-" * 80)

    filtered_projects_query = {
        "StructureLevel": {"type": "PROJECT"},
        "$attributes": {
            "id": 1,
            "name": 1,
            "description": 1,
        },
        "$orderby": {"name": 1},
    }

    print("Filtered query:")
    print(json.dumps(filtered_projects_query, indent=2))

    # Validate
    filtered_validation = JaquelValidator.validate_query(filtered_projects_query)
    print("\nValidation:")
    print(json.dumps(filtered_validation, indent=2))

    # ========================================================================
    # STEP 8: Get operator documentation
    # ========================================================================
    print("\n\nSTEP 8: Get operator documentation for $eq")
    print("-" * 80)

    eq_docs = JaquelValidator.get_operator_info("$eq")
    print("Operator documentation:")
    print(json.dumps(eq_docs, indent=2))

    # ========================================================================
    # FINAL QUERY
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("FINAL QUERY - Ready to use with odsbox!")
    print("=" * 80)

    final_query = filtered_projects_query
    print("\nQuery JSON:")
    print(json.dumps(final_query, indent=2))

    print("\n\nUsage with odsbox:")
    print("-" * 80)
    print(
        """
from odsbox import ConI

with ConI(url="https://docker.peak-solution.de:10032/api",
          auth=("Demo", "mdm")) as con_i:
    
    query = """
        + json.dumps(final_query, indent=6)
        + """
    
    projects = con_i.query(query)
    print(f"Found {len(projects)} projects")
    print(projects)
    """
    )


if __name__ == "__main__":
    asyncio.run(main())
