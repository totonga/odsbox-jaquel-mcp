"""Tests for JaquelExamples."""

from odsbox_jaquel_mcp import JaquelExamples


class TestJaquelExamples:
    """Test cases for JaquelExamples."""

    def test_get_pattern_known_pattern(self):
        """Test getting a known pattern."""
        result = JaquelExamples.get_pattern("get_all_instances")

        assert "template" in result
        assert "description" in result
        assert "explanation" in result
        assert "Get all instances" in result["description"]

    def test_get_pattern_unknown_pattern(self):
        """Test getting an unknown pattern."""
        result = JaquelExamples.get_pattern("unknown_pattern")

        assert "error" in result
        assert "Unknown pattern: unknown_pattern" in result["error"]

    def test_list_patterns(self):
        """Test listing all patterns."""
        patterns = JaquelExamples.list_patterns()

        assert isinstance(patterns, list)
        assert "get_all_instances" in patterns
        assert "get_by_id" in patterns
        assert "get_by_name" in patterns
        assert "case_insensitive_search" in patterns
        assert "time_range" in patterns
        assert "inner_join" in patterns
        assert "outer_join" in patterns
        assert "aggregates" in patterns

    def test_query_generate_skeleton_get_all(self):
        """Test generating get_all skeleton."""
        result = JaquelExamples.query_generate_skeleton("TestEntity", "get_all")

        assert "TestEntity" in result
        assert result["TestEntity"] == {}
        assert "$options" in result
        assert result["$options"]["$rowlimit"] == 5

    def test_query_generate_skeleton_get_by_id(self):
        """Test generating get_by_id skeleton."""
        result = JaquelExamples.query_generate_skeleton("TestEntity", "get_by_id")

        assert "TestEntity" in result
        assert result["TestEntity"] == 123

    def test_query_generate_skeleton_get_by_name(self):
        """Test generating get_by_name skeleton."""
        result = JaquelExamples.query_generate_skeleton("TestEntity", "get_by_name")

        assert "TestEntity" in result
        assert result["TestEntity"] == {"name": "SearchName"}
        assert "$attributes" in result
        assert result["$attributes"] == {"*": 1}

    def test_query_generate_skeleton_search_and_select(self):
        """Test generating search_and_select skeleton."""
        result = JaquelExamples.query_generate_skeleton("TestEntity", "search_and_select")

        assert "TestEntity" in result
        assert result["TestEntity"] == {"name": {"$like": "Search*"}}
        assert "$attributes" in result
        assert "$orderby" in result
        assert "$options" in result
        assert result["$options"]["$rowlimit"] == 10

    def test_query_generate_skeleton_unknown_operation(self):
        """Test generating skeleton with unknown operation."""
        result = JaquelExamples.query_generate_skeleton("TestEntity", "unknown_op")

        assert "error" in result
        assert "Unknown operation: unknown_op" in result["error"]

    def test_query_generate_skeleton_default_operation(self):
        """Test generating skeleton with default operation."""
        result = JaquelExamples.query_generate_skeleton("TestEntity")

        assert "TestEntity" in result
        assert result["TestEntity"] == {}
        assert "$options" in result
        assert result["$options"]["$rowlimit"] == 5
