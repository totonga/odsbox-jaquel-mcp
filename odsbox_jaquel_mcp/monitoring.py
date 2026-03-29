"""Tool and resource call monitoring middleware.

Tracks tool call counts, resource reads, timing, and errors using a
SQLite database for cross-process, cross-platform persistence.

Enable via environment variable ``ODSBOX_STATS_ENABLED=1`` or by
passing ``enabled=True`` to the constructor.  Disabled by default.
"""

from __future__ import annotations

import logging
import os
import platform
import sqlite3
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

_APP_NAME = "odsbox-jaquel-mcp"


_STATS_FILENAME = "odsbox-jaquel-mcp-stats.db"


def _default_stats_path() -> Path:
    """Return a platform-appropriate path for the stats database.

    Tries the platform data directory first, falls back to the system
    temp directory which is always writable.
    """
    candidates: list[Path] = []

    if platform.system() == "Windows":
        base = os.environ.get("APPDATA")
        if base:
            candidates.append(Path(base) / _APP_NAME)
        else:
            candidates.append(Path.home() / "AppData" / "Roaming" / _APP_NAME)
    else:
        # Linux / macOS – XDG convention
        base = os.environ.get("XDG_DATA_HOME")
        if base:
            candidates.append(Path(base) / _APP_NAME)
        else:
            candidates.append(Path.home() / ".local" / "share" / _APP_NAME)

    # Always-writable fallback
    candidates.append(Path(tempfile.gettempdir()))

    for directory in candidates:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            if os.access(directory, os.W_OK):
                return directory / _STATS_FILENAME
        except OSError:
            continue

    # Last resort – current working directory
    return Path.cwd() / _STATS_FILENAME


class ToolStatsMiddleware(Middleware):
    """FastMCP middleware that records tool and resource usage statistics.

    Parameters
    ----------
    stats_file:
        Path to the SQLite database file.  When *None* a platform-specific
        default is used (``~/.local/share/odsbox-jaquel-mcp/stats.db`` on
        Linux, ``%APPDATA%\\odsbox-jaquel-mcp\\stats.db`` on Windows).
    enabled:
        Set to *True* to activate recording.  The environment variable
        ``ODSBOX_STATS_ENABLED=1`` has the same effect.  Disabled by default.
    """

    def __init__(
        self,
        stats_file: str | Path | None = None,
        enabled: bool = False,
    ) -> None:
        self.enabled = enabled or os.environ.get("ODSBOX_STATS_ENABLED", "").strip() in ("1", "true", "yes")

        self._db_path: Path | None = None
        if self.enabled:
            if stats_file is not None:
                self._db_path = Path(stats_file)
            else:
                self._db_path = _default_stats_path()
            self._init_db()

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create the stats database and tables if they don't exist."""
        assert self._db_path is not None
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self._db_path))
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_stats (
                    name        TEXT PRIMARY KEY,
                    calls       INTEGER NOT NULL DEFAULT 0,
                    errors      INTEGER NOT NULL DEFAULT 0,
                    total_ms    REAL    NOT NULL DEFAULT 0.0,
                    last_called TEXT
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS resource_stats (
                    uri         TEXT PRIMARY KEY,
                    reads       INTEGER NOT NULL DEFAULT 0,
                    errors      INTEGER NOT NULL DEFAULT 0,
                    total_ms    REAL    NOT NULL DEFAULT 0.0,
                    last_read   TEXT
                )
                """
            )
            con.commit()
        finally:
            con.close()

    def _record_tool_call(self, name: str, elapsed_ms: float, *, error: bool) -> None:
        now = datetime.now(timezone.utc).isoformat()
        con = sqlite3.connect(str(self._db_path))
        try:
            con.execute(
                """
                INSERT INTO tool_stats (name, calls, errors, total_ms, last_called)
                VALUES (?, 1, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    calls      = calls + 1,
                    errors     = errors + ?,
                    total_ms   = total_ms + ?,
                    last_called = ?
                """,
                (name, int(error), elapsed_ms, now, int(error), elapsed_ms, now),
            )
            con.commit()
        finally:
            con.close()

    def _record_resource_read(self, uri: str, elapsed_ms: float, *, error: bool) -> None:
        now = datetime.now(timezone.utc).isoformat()
        con = sqlite3.connect(str(self._db_path))
        try:
            con.execute(
                """
                INSERT INTO resource_stats (uri, reads, errors, total_ms, last_read)
                VALUES (?, 1, ?, ?, ?)
                ON CONFLICT(uri) DO UPDATE SET
                    reads     = reads + 1,
                    errors    = errors + ?,
                    total_ms  = total_ms + ?,
                    last_read = ?
                """,
                (uri, int(error), elapsed_ms, now, int(error), elapsed_ms, now),
            )
            con.commit()
        finally:
            con.close()

    # ------------------------------------------------------------------
    # Middleware hooks
    # ------------------------------------------------------------------

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        if not self.enabled:
            return await call_next(context)

        tool_name = context.message.name
        start = time.perf_counter()
        error = False
        try:
            result = await call_next(context)
            return result
        except Exception:
            error = True
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            try:
                self._record_tool_call(tool_name, elapsed_ms, error=error)
            except Exception:
                logger.warning("Failed to record tool stats for %s", tool_name, exc_info=True)
            if error:
                logger.info("tool_call name=%s elapsed_ms=%.1f status=error", tool_name, elapsed_ms)
            else:
                logger.info("tool_call name=%s elapsed_ms=%.1f status=ok", tool_name, elapsed_ms)

    async def on_read_resource(self, context: MiddlewareContext, call_next):
        if not self.enabled:
            return await call_next(context)

        uri = str(context.message.uri)
        start = time.perf_counter()
        error = False
        try:
            result = await call_next(context)
            return result
        except Exception:
            error = True
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            try:
                self._record_resource_read(uri, elapsed_ms, error=error)
            except Exception:
                logger.warning("Failed to record resource stats for %s", uri, exc_info=True)
            if error:
                logger.info("resource_read uri=%s elapsed_ms=%.1f status=error", uri, elapsed_ms)
            else:
                logger.info("resource_read uri=%s elapsed_ms=%.1f status=ok", uri, elapsed_ms)
