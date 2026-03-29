"""Tests for ToolStatsMiddleware."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from odsbox_jaquel_mcp.monitoring import ToolStatsMiddleware, _default_stats_path

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


@dataclass
class _FakeMessage:
    """Minimal stand-in for a middleware context message."""

    name: str = ""
    uri: str = ""
    arguments: dict | None = None


@dataclass
class _FakeMiddlewareContext:
    """Minimal stand-in for MiddlewareContext."""

    message: _FakeMessage
    method: str = "tools/call"


def _read_tool_stats(db_path: Path) -> dict:
    """Return tool_stats rows as {name: row_dict}."""
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT * FROM tool_stats").fetchall()
        return {r["name"]: dict(r) for r in rows}
    finally:
        con.close()


def _read_resource_stats(db_path: Path) -> dict:
    """Return resource_stats rows as {uri: row_dict}."""
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT * FROM resource_stats").fetchall()
        return {r["uri"]: dict(r) for r in rows}
    finally:
        con.close()


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestToolStatsMiddlewareInit:
    """Initialisation and disable behaviour."""

    def test_default_stats_path_valid(self):
        p = _default_stats_path()
        assert p is not None
        assert len(p.parts) > 1
        assert p.name == "odsbox-jaquel-mcp-stats.db"

    def test_disabled_by_default(self, tmp_path):
        mw = ToolStatsMiddleware(stats_file=tmp_path / "stats.db")
        assert mw.enabled is False
        assert not (tmp_path / "stats.db").exists()

    def test_enabled_via_constructor(self, tmp_path):
        mw = ToolStatsMiddleware(stats_file=tmp_path / "stats.db", enabled=True)
        assert mw.enabled is True
        assert (tmp_path / "stats.db").exists()

    def test_enabled_via_env_var(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ODSBOX_STATS_ENABLED", "1")
        mw = ToolStatsMiddleware(stats_file=tmp_path / "stats.db")
        assert mw.enabled is True
        assert (tmp_path / "stats.db").exists()

    @pytest.mark.parametrize("val", ["true", "yes", " 1 "])
    def test_enabled_via_env_var_truthy(self, tmp_path, monkeypatch, val):
        monkeypatch.setenv("ODSBOX_STATS_ENABLED", val)
        mw = ToolStatsMiddleware(stats_file=tmp_path / "stats.db")
        assert mw.enabled is True

    def test_env_var_zero_keeps_disabled(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ODSBOX_STATS_ENABLED", "0")
        mw = ToolStatsMiddleware(stats_file=tmp_path / "stats.db")
        assert mw.enabled is False

    def test_creates_parent_dirs(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c" / "stats.db"
        mw = ToolStatsMiddleware(stats_file=deep, enabled=True)
        assert mw.enabled is True
        assert deep.exists()


class TestToolStatsMiddlewareToolCalls:
    """on_call_tool tracking."""

    @pytest.mark.asyncio
    async def test_records_successful_tool_call(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(message=_FakeMessage(name="query_validate"))
        call_next = AsyncMock(return_value="ok")

        result = await mw.on_call_tool(ctx, call_next)

        assert result == "ok"
        call_next.assert_awaited_once_with(ctx)
        stats = _read_tool_stats(db)
        assert "query_validate" in stats
        assert stats["query_validate"]["calls"] == 1
        assert stats["query_validate"]["errors"] == 0
        assert stats["query_validate"]["total_ms"] > 0
        assert stats["query_validate"]["last_called"] is not None

    @pytest.mark.asyncio
    async def test_records_failed_tool_call(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(message=_FakeMessage(name="ods_connect"))
        call_next = AsyncMock(side_effect=RuntimeError("connection failed"))

        with pytest.raises(RuntimeError, match="connection failed"):
            await mw.on_call_tool(ctx, call_next)

        stats = _read_tool_stats(db)
        assert stats["ods_connect"]["calls"] == 1
        assert stats["ods_connect"]["errors"] == 1

    @pytest.mark.asyncio
    async def test_increments_on_repeated_calls(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(message=_FakeMessage(name="schema_get_entity"))
        call_next = AsyncMock(return_value="ok")

        for _ in range(5):
            await mw.on_call_tool(ctx, call_next)

        stats = _read_tool_stats(db)
        assert stats["schema_get_entity"]["calls"] == 5
        assert stats["schema_get_entity"]["errors"] == 0

    @pytest.mark.asyncio
    async def test_tracks_multiple_tools(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        call_next = AsyncMock(return_value="ok")

        for name in ("tool_a", "tool_b", "tool_a"):
            ctx = _FakeMiddlewareContext(message=_FakeMessage(name=name))
            await mw.on_call_tool(ctx, call_next)

        stats = _read_tool_stats(db)
        assert stats["tool_a"]["calls"] == 2
        assert stats["tool_b"]["calls"] == 1

    @pytest.mark.asyncio
    async def test_disabled_middleware_is_noop(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=False)
        ctx = _FakeMiddlewareContext(message=_FakeMessage(name="query_validate"))
        call_next = AsyncMock(return_value="ok")

        result = await mw.on_call_tool(ctx, call_next)

        assert result == "ok"
        call_next.assert_awaited_once_with(ctx)
        assert not db.exists()


class TestToolStatsMiddlewareResourceReads:
    """on_read_resource tracking."""

    @pytest.mark.asyncio
    async def test_records_successful_resource_read(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(
            message=_FakeMessage(uri="guide://jaquel-syntax"),
            method="resources/read",
        )
        call_next = AsyncMock(return_value="content")

        result = await mw.on_read_resource(ctx, call_next)

        assert result == "content"
        stats = _read_resource_stats(db)
        assert "guide://jaquel-syntax" in stats
        assert stats["guide://jaquel-syntax"]["reads"] == 1
        assert stats["guide://jaquel-syntax"]["errors"] == 0

    @pytest.mark.asyncio
    async def test_records_failed_resource_read(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(
            message=_FakeMessage(uri="guide://missing"),
            method="resources/read",
        )
        call_next = AsyncMock(side_effect=FileNotFoundError("not found"))

        with pytest.raises(FileNotFoundError):
            await mw.on_read_resource(ctx, call_next)

        stats = _read_resource_stats(db)
        assert stats["guide://missing"]["reads"] == 1
        assert stats["guide://missing"]["errors"] == 1

    @pytest.mark.asyncio
    async def test_disabled_middleware_skips_resource_read(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=False)
        ctx = _FakeMiddlewareContext(
            message=_FakeMessage(uri="guide://test"),
            method="resources/read",
        )
        call_next = AsyncMock(return_value="content")

        result = await mw.on_read_resource(ctx, call_next)

        assert result == "content"
        assert not db.exists()


class TestToolStatsMiddlewarePersistence:
    """Cross-session persistence via SQLite."""

    @pytest.mark.asyncio
    async def test_stats_survive_new_middleware_instance(self, tmp_path):
        db = tmp_path / "stats.db"

        # Session 1: make some calls
        mw1 = ToolStatsMiddleware(stats_file=db, enabled=True)
        ctx = _FakeMiddlewareContext(message=_FakeMessage(name="query_validate"))
        call_next = AsyncMock(return_value="ok")
        await mw1.on_call_tool(ctx, call_next)
        await mw1.on_call_tool(ctx, call_next)

        # Session 2: new instance, same db
        mw2 = ToolStatsMiddleware(stats_file=db, enabled=True)
        await mw2.on_call_tool(ctx, call_next)

        stats = _read_tool_stats(db)
        assert stats["query_validate"]["calls"] == 3

    @pytest.mark.asyncio
    async def test_mixed_tool_and_resource_persistence(self, tmp_path):
        db = tmp_path / "stats.db"
        mw = ToolStatsMiddleware(stats_file=db, enabled=True)
        call_next = AsyncMock(return_value="ok")

        tool_ctx = _FakeMiddlewareContext(message=_FakeMessage(name="tool_x"))
        res_ctx = _FakeMiddlewareContext(
            message=_FakeMessage(uri="guide://syntax"),
            method="resources/read",
        )

        await mw.on_call_tool(tool_ctx, call_next)
        await mw.on_read_resource(res_ctx, call_next)

        assert len(_read_tool_stats(db)) == 1
        assert len(_read_resource_stats(db)) == 1
