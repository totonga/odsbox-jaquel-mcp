"""Tests for JaquelValidator."""

from odsbox_jaquel_mcp import JaquelValidator


class TestJaquelValidator:
    """Test cases for JaquelValidator."""

    def test_validate_query_invalid_type(self):
        """Test validation of non-dict query."""
        result = JaquelValidator.validate_query("not a dict")

        assert result["valid"] is False
        assert "Query must be a dictionary" in result["errors"]

    def test_validate_query_no_entity(self):
        """Test validation of query with no entity name."""
        query = {"$attributes": {"name": 1}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "Query must contain an entity name" in result["errors"][0]

    def test_validate_query_multiple_entities(self):
        """Test validation of query with multiple non-$ entities."""
        query = {"Entity1": {}, "Entity2": {}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "Query is only allowed to contain a single non-$ element" in result["errors"][0]
        assert "Entity1" in result["errors"][0]
        assert "Entity2" in result["errors"][0]

    def test_validate_query_valid_simple(self):
        """Test validation of simple valid query."""
        query = {"TestEntity": {}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []
        assert result["suggestions"] == []

    def test_validate_query_entity_none_value(self):
        """Test validation when entity value is None."""
        query = {"TestEntity": None}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "query value cannot be None" in result["errors"][0]

    def test_validate_query_entity_invalid_value_type(self):
        """Test validation when entity value has invalid type."""
        query = {"TestEntity": []}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "query value must be dict, int, or string" in result["errors"][0]

    def test_validate_query_unknown_special_key(self):
        """Test validation with unknown special key."""
        query = {"TestEntity": {}, "$unknown": "value"}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is True
        assert "Unknown special key: $unknown" in result["warnings"]

    def test_validate_query_empty_attributes(self):
        """Test validation with empty $attributes."""
        query = {"TestEntity": {}, "$attributes": {}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is True
        assert "consider removing it or adding attributes" in result["suggestions"][0]

    def test_validate_query_invalid_attributes_type(self):
        """Test validation with invalid $attributes type."""
        query = {"TestEntity": {}, "$attributes": "invalid"}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "$attributes must be a dictionary" in result["errors"]

    def test_validate_query_invalid_orderby_type(self):
        """Test validation with invalid $orderby type."""
        query = {"TestEntity": {}, "$orderby": "invalid"}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "$orderby must be a dictionary" in result["errors"][0]

    def test_validate_query_invalid_groupby_type(self):
        """Test validation with invalid $groupby type."""
        query = {"TestEntity": {}, "$groupby": "invalid"}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "$groupby must be a dictionary" in result["errors"]

    def test_validate_query_invalid_rowlimit_type(self):
        """Test validation with invalid $rowlimit type."""
        query = {"TestEntity": {}, "$options": {"$rowlimit": "invalid"}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "$rowlimit must be an integer" in result["errors"]

    def test_validate_query_invalid_rowskip_type(self):
        """Test validation with invalid $rowskip type."""
        query = {"TestEntity": {}, "$options": {"$rowskip": "invalid"}}
        result = JaquelValidator.validate_query(query)

        assert result["valid"] is False
        assert "$rowskip must be an integer" in result["errors"]

    def test_validate_filter_condition_valid_simple(self):
        """Test validation of simple valid filter condition."""
        condition = {"name": {"$eq": "test"}}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_filter_condition_valid_simple2(self):
        """Test validation of simple valid filter condition."""
        condition = {"name": "test"}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_filter_condition_valid_simple3(self):
        """Test validation of simple valid filter condition."""
        condition = {"state": 123}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_filter_condition_unknown_operator(self):
        """Test validation with unknown operator."""
        condition = {"name": {"$unknown": "value"}}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is False
        assert "Unknown operator: $unknown" in result["errors"][0]

    def test_validate_filter_condition_invalid_null_value(self):
        """Test validation of $null with invalid value."""
        condition = {"field": {"$null": 0}}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is True
        assert "$null should have value 1" in result["warnings"][0]

    def test_validate_filter_condition_invalid_between_type(self):
        """Test validation of $between with non-list value."""
        condition = {"field": {"$between": "not a list"}}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is False
        assert "$between requires a list value" in result["errors"][0]

    def test_validate_filter_condition_invalid_and_type(self):
        """Test validation of $and with non-list value."""
        condition = {"$and": "not a list"}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is False
        assert "$and must contain an array at 'AoTest'" in result["errors"]

    def test_validate_filter_condition_invalid_not_type(self):
        """Test validation of $not with non-dict value."""
        condition = {"$not": "not a dict"}
        result = JaquelValidator.validate_query({"AoTest": condition})

        assert result["valid"] is False
        assert "$not must contain expression at 'AoTest'" in result["errors"]

    def test_get_operator_info_known_operator(self):
        """Test getting info for known operator."""
        result = JaquelValidator.get_operator_info("$eq")

        assert "category" in result
        assert result["category"] == "comparison"
        assert "description" in result
        assert "example" in result

    def test_get_operator_info_unknown_operator(self):
        """Test getting info for unknown operator."""
        result = JaquelValidator.get_operator_info("$unknown")

        assert "error" in result
        assert "Unknown operator: $unknown" in result["error"]

    def test_get_operator_info_like_with_options(self):
        """Test getting info for $like operator with options."""
        result = JaquelValidator.get_operator_info("$like")

        assert result["category"] == "comparison"
        assert "options" in result
        assert "case-insensitive" in result["options"]

    def test_get_operator_info_aggregate_function(self):
        """Test getting info for aggregate function."""
        result = JaquelValidator.get_operator_info("$min")

        assert result["category"] == "aggregate"
        assert "minimum value" in result["description"]
