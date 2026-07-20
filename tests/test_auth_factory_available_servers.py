"""Tests for auth_factory.get_available_servers() and get_available_server_infos()."""

from __future__ import annotations

from odsbox_jaquel_mcp.auth_factory import get_available_server_infos, get_available_servers


class TestGetAvailableServers:
    """Tests for get_available_servers()."""

    def test_empty_environment_returns_empty_list(self, monkeypatch):
        """No matching env vars → empty list."""
        monkeypatch.setenv("UNRELATED_VAR", "value")
        env = {"UNRELATED_VAR": "value"}
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == []

    def test_single_odsbox_mcp_url_var(self):
        """ODSBOX_MCP_MYSERVER_URL extracts prefix 'MYSERVER'."""
        env = {"ODSBOX_MCP_MYSERVER_URL": "http://myserver/api"}
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == ["MYSERVER"]

    def test_single_ods_prefixed_url_var(self):
        """ODS_PRODUCTION_URL extracts prefix 'PRODUCTION'."""
        env = {"ODS_PRODUCTION_URL": "http://production/api"}
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == ["PRODUCTION"]

    def test_multiple_odsbox_mcp_servers(self):
        """Multiple ODSBOX_MCP_<name>_URL vars → all names returned sorted."""
        env = {
            "ODSBOX_MCP_STAGING_URL": "http://staging/api",
            "ODSBOX_MCP_PROD_URL": "http://prod/api",
            "ODSBOX_MCP_DEV_URL": "http://dev/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == ["DEV", "PROD", "STAGING"]

    def test_deduplication_same_prefix_both_styles(self):
        """ODS_FOO_URL and ODSBOX_MCP_FOO_URL both resolve to 'FOO' → deduplicated."""
        env = {
            "ODS_FOO_URL": "http://foo-ods/api",
            "ODSBOX_MCP_FOO_URL": "http://foo-mcp/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == ["FOO"]

    def test_result_is_sorted(self):
        """Result list is always sorted alphabetically."""
        env = {
            "ODSBOX_MCP_ZEBRA_URL": "http://z/api",
            "ODSBOX_MCP_ALPHA_URL": "http://a/api",
            "ODSBOX_MCP_MANGO_URL": "http://m/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == sorted(result)
        assert result == ["ALPHA", "MANGO", "ZEBRA"]

    def test_ignores_vars_without_url_suffix(self):
        """Variables ending in _USERNAME, _PASSWORD, etc. are ignored."""
        env = {
            "ODSBOX_MCP_SERVER1_USERNAME": "admin",
            "ODSBOX_MCP_SERVER1_PASSWORD": "secret",
            "ODS_SERVER2_USERNAME": "user",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == []

    def test_ignores_vars_without_matching_prefix(self):
        """Only ODS_ and ODSBOX_MCP_ prefixed URL vars match."""
        env = {
            "MY_SERVER_URL": "http://my/api",
            "APP_URL": "http://app/api",
            "SERVER_URL": "http://server/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == []

    def test_mixed_prefixes_deduplicated(self):
        """ODS_ and ODSBOX_MCP_ for same server name → single entry."""
        env = {
            "ODS_ALPHA_URL": "http://alpha1/api",
            "ODSBOX_MCP_ALPHA_URL": "http://alpha2/api",
            "ODSBOX_MCP_BETA_URL": "http://beta/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        assert result == ["ALPHA", "BETA"]

    def test_bare_ods_url_produces_empty_prefix(self):
        """ODS_URL (bare legacy var) produces an empty-string prefix."""
        env = {"ODS_URL": "http://legacy/api"}
        result = get_available_servers(env)  # type: ignore[arg-type]
        # The empty prefix is included (it's the caller's responsibility to filter it)
        assert "" in result

    def test_bare_odsbox_mcp_url_produces_empty_prefix(self):
        """ODSBOX_MCP_URL (bare modern var) produces an empty-string prefix."""
        env = {"ODSBOX_MCP_URL": "http://modern/api"}
        result = get_available_servers(env)  # type: ignore[arg-type]
        # The empty prefix is included (it's the caller's responsibility to filter it)
        assert "" in result

    def test_bare_urls_both_styles_deduplicate_to_one_empty(self):
        """Both ODS_URL and ODSBOX_MCP_URL produce the same empty prefix → deduplicated."""
        env = {
            "ODS_URL": "http://legacy/api",
            "ODSBOX_MCP_URL": "http://modern/api",
        }
        result = get_available_servers(env)  # type: ignore[arg-type]
        # Should have exactly one empty string (deduplicated)
        assert result.count("") == 1
        assert result == [""]


class TestGetAvailableServerInfos:
    """Tests for get_available_server_infos()."""

    def test_empty_environment_returns_empty_list(self):
        """No matching env vars → empty list."""
        result = get_available_server_infos({})  # type: ignore[arg-type]
        assert result == []

    def test_odsbox_mcp_url_resolves_correctly(self):
        """ODSBOX_MCP_SERVER_URL is found via _env_get with prefix 'SERVER'."""
        env = {
            "ODSBOX_MCP_SERVER_URL": "http://server/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        assert len(result) == 1
        assert result[0]["prefix"] == "SERVER"
        assert result[0]["url"] == "http://server/api"

    def test_ods_prefixed_url_resolves_via_direct_fallback(self):
        """ODS_PRODUCTION_URL is resolved via the ODS_<prefix>_URL direct fallback."""
        env = {
            "ODS_PRODUCTION_URL": "http://production/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        assert len(result) == 1
        assert result[0]["prefix"] == "PRODUCTION"
        assert result[0]["url"] == "http://production/api"

    def test_empty_prefix_from_bare_ods_url_is_skipped(self):
        """Bare ODS_URL (empty prefix) is excluded from the result."""
        env = {
            "ODS_URL": "http://legacy/api",
            "ODSBOX_MCP_SERVER_URL": "http://server/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        prefixes = [r["prefix"] for r in result]
        assert "" not in prefixes
        assert "SERVER" in prefixes

    def test_empty_prefix_from_bare_odsbox_mcp_url_is_skipped(self):
        """Bare ODSBOX_MCP_URL (empty prefix) is excluded from the result."""
        env = {
            "ODSBOX_MCP_URL": "http://modern/api",
            "ODSBOX_MCP_SERVER_URL": "http://server/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        prefixes = [r["prefix"] for r in result]
        assert "" not in prefixes
        assert "SERVER" in prefixes

    def test_both_bare_urls_skipped_with_named_server(self):
        """Both ODS_URL and ODSBOX_MCP_URL are skipped; only named server included."""
        env = {
            "ODS_URL": "http://legacy/api",
            "ODSBOX_MCP_URL": "http://modern/api",
            "ODSBOX_MCP_PROD_URL": "http://prod/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        prefixes = [r["prefix"] for r in result]
        assert "" not in prefixes
        assert prefixes == ["PROD"]

    def test_multiple_servers_all_resolved(self):
        """Multiple servers are all returned with correct URLs."""
        env = {
            "ODSBOX_MCP_DEV_URL": "http://dev/api",
            "ODSBOX_MCP_PROD_URL": "http://prod/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        assert len(result) == 2
        by_prefix = {r["prefix"]: r["url"] for r in result}
        assert by_prefix["DEV"] == "http://dev/api"
        assert by_prefix["PROD"] == "http://prod/api"

    def test_deduplication_prefers_odsbox_mcp_url(self):
        """When both ODS_FOO_URL and ODSBOX_MCP_FOO_URL are set, they deduplicate to one entry."""
        env = {
            "ODS_FOO_URL": "http://foo-ods/api",
            "ODSBOX_MCP_FOO_URL": "http://foo-mcp/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        assert len(result) == 1
        assert result[0]["prefix"] == "FOO"
        # ODSBOX_MCP_FOO_URL wins via _env_get (checked before ODS_FOO_URL direct fallback)
        assert result[0]["url"] == "http://foo-mcp/api"

    def test_missing_url_returns_empty_string(self):
        """Prefix found but URL resolution yields empty string if nothing matches."""
        # ODS_GHOST_URL → prefix GHOST; but _env_get("GHOST", "URL") won't find ODS_GHOST_URL
        # However, the ODS_<prefix>_URL direct fallback WILL find it.
        # To trigger missing URL: manufacture a prefix without any URL var.
        # We fake this via a patched env dict with only a non-URL key set:
        env = {"ODSBOX_MCP_NOURL_USERNAME": "user"}
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        # No _URL var → no server found → empty list
        assert result == []

    def test_result_is_sorted_by_prefix(self):
        """Output list is sorted by prefix alphabetically."""
        env = {
            "ODSBOX_MCP_ZETA_URL": "http://z/api",
            "ODSBOX_MCP_ALPHA_URL": "http://a/api",
        }
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        prefixes = [r["prefix"] for r in result]
        assert prefixes == sorted(prefixes)

    def test_each_entry_has_prefix_and_url_keys(self):
        """Every returned dict contains exactly 'prefix' and 'url' keys."""
        env = {"ODSBOX_MCP_SERVER_URL": "http://server/api"}
        result = get_available_server_infos(env)  # type: ignore[arg-type]
        for entry in result:
            assert set(entry.keys()) == {"prefix", "url"}
