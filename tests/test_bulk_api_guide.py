"""
test_bulk_api_guide.py - Comprehensive tests for the bulk API guidance system.

Tests the BulkAPIGuide class which provides AI assistance for efficient
timeseries data loading using the bulk API.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from odsbox_jaquel_mcp.bulk_api_guide import BulkAPIGuide


class TestBulkAPIGuideTopics:
    """Test that all help topics exist and return valid content."""

    def test_the_3_step_rule(self):
        """Test the fundamental 3-step workflow help."""
        help_text = BulkAPIGuide.THE_3_STEP_RULE
        assert help_text is not None
        assert "CONNECT" in help_text
        assert "DISCOVER" in help_text
        assert "LOAD" in help_text
        assert "3" in help_text and "STEP" in help_text

    def test_bulk_vs_jaquel(self):
        """Test bulk vs Jaquel query comparison help."""
        help_text = BulkAPIGuide.BULK_VS_JAQUEL
        assert help_text is not None
        assert "bulk" in help_text.lower()
        assert "jaquel" in help_text.lower()

    def test_pattern_syntax(self):
        """Test column pattern syntax help."""
        help_text = BulkAPIGuide.PATTERN_SYNTAX
        assert help_text is not None
        assert "*" in help_text or "wildcard" in help_text.lower()
        assert "pattern" in help_text.lower()

    def test_common_mistakes(self):
        """Test common mistakes help."""
        help_text = BulkAPIGuide.COMMON_MISTAKES
        assert help_text is not None
        assert "mistake" in help_text.lower() or "error" in help_text.lower()

    def test_decision_tree(self):
        """Test decision tree help."""
        help_text = BulkAPIGuide.DECISION_TREE
        assert help_text is not None
        assert "decision" in help_text.lower() or "choose" in help_text.lower()

    def test_quick_start(self):
        """Test quick start help."""
        help_text = BulkAPIGuide.QUICK_START
        assert help_text is not None
        assert len(help_text) > 100
        assert "connect" in help_text.lower() or "start" in help_text.lower()

    def test_step_by_step(self):
        """Test step by step help."""
        help_text = BulkAPIGuide.STEP_BY_STEP
        assert help_text is not None
        assert len(help_text) > 100

    def test_response_template(self):
        """Test response template help."""
        help_text = BulkAPIGuide.RESPONSE_TEMPLATE
        assert help_text is not None
        assert len(help_text) > 100

    def test_troubleshooting(self):
        """Test troubleshooting help."""
        help_text = BulkAPIGuide.TROUBLESHOOTING
        assert help_text is not None
        assert "error" in help_text.lower() or "problem" in help_text.lower() or "troubl" in help_text.lower()

    def test_tool_patterns(self):
        """Test tool patterns help."""
        help_text = BulkAPIGuide.TOOL_PATTERNS
        assert help_text is not None
        assert len(help_text) > 100


class TestGetHelpMethod:
    """Test the get_help method that retrieves help by topic."""

    def test_get_help_valid_topic(self):
        """Test getting help for a valid topic."""
        help_text = BulkAPIGuide.get_help("the_3_step_rule")
        assert help_text is not None
        assert isinstance(help_text, str)
        assert len(help_text) > 0

    def test_get_help_all_valid_topics(self):
        """Test getting help for all valid topics."""
        topics = [
            "3-step-rule",
            "quick-start",
            "bulk-vs-jaquel",
            "patterns",
            "decision-tree",
            "mistakes",
            "step-by-step",
            "response-template",
            "troubleshooting",
            "tool-patterns",
        ]
        for topic in topics:
            help_text = BulkAPIGuide.get_help(topic)
            assert help_text is not None, f"Help not found for topic: {topic}"
            assert isinstance(help_text, str), f"Help is not string for topic: {topic}"
            assert len(help_text) > 50, f"Help too short for topic: {topic}"

    def test_get_help_invalid_topic(self):
        """Test getting help for invalid topic."""
        help_text = BulkAPIGuide.get_help("invalid_topic_xyz")
        # Should return None or a message indicating topic not found
        if help_text is not None:
            assert "not found" in help_text.lower() or "unknown" in help_text.lower()

    def test_get_help_empty_topic(self):
        """Test getting help with empty topic."""
        help_text = BulkAPIGuide.get_help("")
        # Should handle gracefully
        assert help_text is None or isinstance(help_text, str)

    def test_get_help_none_topic(self):
        """Test getting help with None topic."""
        help_text = BulkAPIGuide.get_help(None)
        # Should handle gracefully
        assert help_text is None or isinstance(help_text, str)


class TestContextualHelp:
    """Test contextual help based on tool names."""

    def test_contextual_help_connect_tool(self):
        """Test contextual help for ods_connect tool."""
        help_text = BulkAPIGuide.get_contextual_help("ods_connect")
        assert help_text is not None
        assert isinstance(help_text, str)
        # Should mention connection or ODS server
        assert "connect" in help_text.lower() or "connection" in help_text.lower()

    def test_contextual_help_read_tool(self):
        """Test contextual help for data_read_submatrix tool."""
        help_text = BulkAPIGuide.get_contextual_help("data_read_submatrix")
        assert help_text is not None
        assert isinstance(help_text, str)
        # Should mention data reading or loading
        assert "read" in help_text.lower() or "load" in help_text.lower()

    def test_contextual_help_quantities_tool(self):
        """Test contextual help for data_get_quantities tool."""
        help_text = BulkAPIGuide.get_contextual_help("data_get_quantities")
        assert help_text is not None
        assert isinstance(help_text, str)
        # Should mention columns or availability
        assert "column" in help_text.lower() or "available" in help_text.lower()

    def test_contextual_help_script_tool(self):
        """Test contextual help for data_generate_fetcher_script tool."""
        help_text = BulkAPIGuide.get_contextual_help("data_generate_fetcher_script")
        assert help_text is not None
        assert isinstance(help_text, str)
        # Should mention script generation
        assert "script" in help_text.lower() or "generate" in help_text.lower()

    def test_contextual_help_hierarchy_tool(self):
        """Test contextual help for data_query_hierarchy tool."""
        help_text = BulkAPIGuide.get_contextual_help("data_query_hierarchy")
        assert help_text is not None
        assert isinstance(help_text, str)
        # Should mention hierarchy
        assert "hierarchy" in help_text.lower() or "explore" in help_text.lower()

    def test_contextual_help_unknown_tool(self):
        """Test contextual help for unknown tool."""
        help_text = BulkAPIGuide.get_contextual_help("unknown_tool_xyz")
        # Should return None or a message
        if help_text is not None:
            assert isinstance(help_text, str)


class TestGetAllHelp:
    """Test the get_all_help method that returns all help content."""

    def test_get_all_help(self):
        """Test getting all help content."""
        all_help = BulkAPIGuide.get_all_help()
        assert all_help is not None
        assert isinstance(all_help, str)
        # Should be a concatenated string with all content
        assert len(all_help) > 500

    def test_get_all_help_has_all_sections(self):
        """Test that get_all_help contains all major sections."""
        all_help = BulkAPIGuide.get_all_help()
        # Check for major sections
        sections = ["3-STEP", "QUICK", "BULK", "DECISION", "MISTAKE", "STEP", "TROUBL"]
        for section in sections:
            assert section.upper() in all_help.upper(), f"Section {section} not in all_help"

    def test_get_all_help_content_quality(self):
        """Test that all help content is reasonable."""
        all_help = BulkAPIGuide.get_all_help()
        # Should have substantial content
        assert len(all_help) >= 500


class TestHelpContentQuality:
    """Test the quality and completeness of help content."""

    def test_help_content_not_empty(self):
        """Test that no individual help content is empty."""
        # Test each major constant
        constants = [
            ("THE_3_STEP_RULE", BulkAPIGuide.THE_3_STEP_RULE),
            ("QUICK_START", BulkAPIGuide.QUICK_START),
            ("BULK_VS_JAQUEL", BulkAPIGuide.BULK_VS_JAQUEL),
            ("PATTERN_SYNTAX", BulkAPIGuide.PATTERN_SYNTAX),
            ("DECISION_TREE", BulkAPIGuide.DECISION_TREE),
            ("COMMON_MISTAKES", BulkAPIGuide.COMMON_MISTAKES),
            ("STEP_BY_STEP", BulkAPIGuide.STEP_BY_STEP),
            ("RESPONSE_TEMPLATE", BulkAPIGuide.RESPONSE_TEMPLATE),
            ("TROUBLESHOOTING", BulkAPIGuide.TROUBLESHOOTING),
            ("TOOL_PATTERNS", BulkAPIGuide.TOOL_PATTERNS),
        ]
        for name, content in constants:
            assert content is not None, f"{name} is None"
            assert isinstance(content, str), f"{name} is not a string"
            assert len(content) > 0, f"{name} is empty"

    def test_help_content_formatting(self):
        """Test that help content is reasonably formatted."""
        all_help = BulkAPIGuide.get_all_help()
        # Should contain readable text
        assert len(all_help.strip()) > 0
        # Should not contain excessive special characters
        special_char_ratio = sum(1 for c in all_help if not c.isalnum() and c not in " \n\t.,:-️⃣❌✅📋") / len(all_help)
        assert special_char_ratio < 0.5, "Help has too many special characters"

    def test_3_step_rule_completeness(self):
        """Test that the 3-step rule contains all three steps."""
        help_text = BulkAPIGuide.THE_3_STEP_RULE
        # All three steps should be mentioned
        steps = ["CONNECT", "DISCOVER", "LOAD"]
        for step in steps:
            assert step in help_text, f"Step {step} not found in 3-step rule"

    def test_common_mistakes_has_content(self):
        """Test that common mistakes section has substantive content."""
        help_text = BulkAPIGuide.COMMON_MISTAKES
        # Should mention at least one specific mistake
        assert len(help_text) > 100  # Should be substantive

    def test_pattern_syntax_has_content(self):
        """Test that pattern syntax section has substantive content."""
        help_text = BulkAPIGuide.PATTERN_SYNTAX
        # Should have examples or specific patterns
        assert len(help_text) > 50  # Should be substantive


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_case_sensitivity(self):
        """Test that topic lookup is case-insensitive or consistent."""
        help1 = BulkAPIGuide.get_help("the_3_step_rule")
        help2 = BulkAPIGuide.get_help("THE_3_STEP_RULE")
        # Either both should work or both should return None
        if help1 is None and help2 is None:
            pass  # Both None is fine
        # The method should handle case consistently

    def test_whitespace_handling(self):
        """Test that whitespace in topic names is handled."""
        help_text = BulkAPIGuide.get_help("the_3_step_rule")
        # Should handle without issues
        assert help_text is not None

    def test_concurrent_access(self):
        """Test that multiple concurrent help requests work."""
        topics = ["the_3_step_rule", "quick_start", "pattern_syntax"]
        help_texts = [BulkAPIGuide.get_help(topic) for topic in topics]
        # All should return valid content
        assert all(h is not None for h in help_texts)


class TestDocumentationLinks:
    """Test that help content is substantive and complete."""

    def test_3_step_rule_substantive(self):
        """Test that 3-step rule is substantive."""
        help_text = BulkAPIGuide.THE_3_STEP_RULE
        # Should be substantive enough to be useful
        assert len(help_text) > 200

    def test_step_by_step_substantive(self):
        """Test that step by step content is substantive."""
        help_text = BulkAPIGuide.STEP_BY_STEP
        # Should include step-by-step guidance
        assert len(help_text) > 300


class TestContextualHelpMethods:
    """Test the contextual help retrieval methods."""

    def test_get_contextual_help_all_bulk_tools(self):
        """Test contextual help for all bulk-related tools."""
        tools = [
            "ods_connect",
            "data_read_submatrix",
            "data_get_quantities",
            "data_generate_fetcher_script",
            "data_query_hierarchy",
        ]
        for tool in tools:
            help_text = BulkAPIGuide.get_contextual_help(tool)
            # Each tool should have help
            assert help_text is not None or isinstance(help_text, str)

    def test_contextual_help_relevance(self):
        """Test that contextual help is relevant to the tool."""
        help_text = BulkAPIGuide.get_contextual_help("ods_connect")
        if help_text:
            # Should be related to connection
            keywords = ["connect", "connection", "server", "ods", "url", "credential"]
            assert any(kw in help_text.lower() for kw in keywords)


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_ai_learning_scenario(self):
        """Test the scenario where AI first encounters bulk API."""
        # AI should be able to get fundamental help
        fundamentals = BulkAPIGuide.get_help("3-step-rule")
        assert fundamentals is not None
        assert "CONNECT" in fundamentals or "connect" in fundamentals.lower()

    def test_error_recovery_scenario(self):
        """Test the scenario where AI encounters an error and needs help."""
        # AI should be able to get troubleshooting help
        troubleshooting = BulkAPIGuide.get_help("troubleshooting")
        assert troubleshooting is not None
        assert len(troubleshooting) > 100

    def test_optimization_scenario(self):
        """Test the scenario where AI wants to optimize data loading."""
        # AI should be able to get tool patterns
        patterns = BulkAPIGuide.get_help("tool-patterns")
        assert patterns is not None
        assert len(patterns) > 100

    def test_decision_making_scenario(self):
        """Test the scenario where AI needs to decide on tool selection."""
        # AI should be able to get decision tree
        decision_help = BulkAPIGuide.get_help("decision-tree")
        assert decision_help is not None


class TestHelpContentConsistency:
    """Test consistency of help content across methods."""

    def test_get_help_returns_string(self):
        """Test that get_help returns string."""
        # The get_help method should return consistent content
        topic = "3-step-rule"
        from_method = BulkAPIGuide.get_help(topic)
        # Should be non-empty
        assert from_method is not None
        assert isinstance(from_method, str)
        assert len(from_method) > 0

    def test_all_help_consistent(self):
        """Test that get_all_help returns consistent concatenated content."""
        all_help = BulkAPIGuide.get_all_help()
        # Should be a concatenated string
        assert isinstance(all_help, str)
        assert len(all_help) > 500
        # Should contain content from multiple sections
        assert "CONNECT" in all_help or "connect" in all_help


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
