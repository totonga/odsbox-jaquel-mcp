"""ODS Connection Manager for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp.exceptions import ToolError
from odsbox import ConI
from odsbox.con_i_factory import ConIFactory
from odsbox.model_cache import ModelCache
from odsbox.proto import ods

from .schemas_types import ConnectionInfo, ConnectResult


def _build_code_example(
    mode: str,
    url: str,
    username: str = "",
    token_endpoint: str = "",
    client_id: str = "",
    redirect_uri: str = "",
) -> str:
    """Generate a compact Python script example for connecting to the ODS server."""
    q = '{"AoTest": {}, "$attributes": {"id": 1, "name": 1}}'
    if mode == "basic":
        return (
            f"import keyring\nfrom odsbox import ConIFactory\n\n"
            f"url = {url!r}\nusername = {username!r}\n"
            f"password = keyring.get_password(url, username)\n"
            f"with ConIFactory.basic(url=url, username=username, password=password,\n"
            f"                       verify_certificate=True) as con_i:\n"
            f"    result = con_i.query({q})\n"
        )
    if mode == "m2m":
        return (
            f"import keyring\nfrom odsbox import ConIFactory\n\n"
            f"url = {url!r}\ntoken_endpoint = {token_endpoint!r}\nclient_id = {client_id!r}\n"
            f"client_secret = keyring.get_password(token_endpoint, client_id)\n"
            f"with ConIFactory.m2m(url=url, token_endpoint=token_endpoint, client_id=client_id,\n"
            f"                     client_secret=client_secret, verify_certificate=True) as con_i:\n"
            f"    result = con_i.query({q})\n"
        )
    if mode == "oidc":
        return (
            f"from odsbox import ConIFactory\n\n"
            f"url = {url!r}\n"
            f"with ConIFactory.oidc(url=url, client_id={client_id!r},\n"
            f"                      redirect_uri={redirect_uri!r}, verify_certificate=True) as con_i:\n"
            f"    result = con_i.query({q})\n"
        )
    return ""


class ODSConnectionManager:
    """Manages connection to ASAM ODS server and provides model access."""

    _instance: ODSConnectionManager | None = None
    _con_i: ConI | None = None
    _model_cache: ModelCache | None = None
    _model: ods.Model | None = None
    _connection_info: ConnectionInfo | None = None

    def __init__(self):
        """Initialize connection manager (singleton)."""
        pass

    def __del__(self):
        """Ensure connection is closed on cleanup."""
        try:
            if self._con_i:
                self._con_i.close()
        except Exception:
            pass

    @classmethod
    def get_instance(cls) -> ODSConnectionManager:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _init_from_con_i(
        cls, con_i: ConI, base_url: str, display_username: str, code_example: str = ""
    ) -> ConnectResult:
        """Initialize connection state from an already-created ConI instance.

        Shared helper used by both ``connect()`` and ``connect_with_factory()``.
        Loads the model, populates ``_connection_info``, and returns a ConnectResult.
        """
        instance = cls.get_instance()

        # Close existing connection if any
        if instance._con_i:
            try:
                instance._con_i.close()
            except Exception:
                pass

        instance._con_i = con_i
        instance._model_cache = con_i.mc
        instance._model = con_i.model()

        ao_test_entity_name = "AoTest"
        if instance._model is not None and instance._model.entities is not None:
            for _e_name, e in instance._model.entities.items():
                if e.base_name.lower() == "aotest":
                    ao_test_entity_name = e.name
                    break

        initial_query = {
            ao_test_entity_name: {"name": {"$like": "*"}},
            "$attributes": {"id": 1, "name": 1},
            "$options": {"$rowlimit": 100},
        }

        instance._connection_info = ConnectionInfo(
            url=base_url,
            username=display_username,
            con_i_url=con_i.con_i_url(),
            status="connected",
            available_entities=list(instance._model.entities.keys()) if instance._model else [],
            initial_query=initial_query,
            code_example=code_example,
        )

        return ConnectResult(message="Connected to ODS server", connection=instance._connection_info)

    @classmethod
    def connect(cls, url: str, auth: tuple, **kwargs) -> ConnectResult:
        """Establish connection to ODS server.

        Args:
            url: ODS API URL (e.g., http://localhost:8087/api)
            auth: (username, password) tuple
            **kwargs: Additional ConI parameters

        Returns:
            ConnectResult with message and ConnectionInfo
        """
        try:
            con_i = ConI(url=url, auth=auth, load_model=True, **kwargs)
            display_username = auth[0] if isinstance(auth, tuple) else "unknown"
            code_example = _build_code_example("basic", url, username=display_username)
            return cls._init_from_con_i(
                con_i=con_i, base_url=url, display_username=display_username, code_example=code_example
            )
        except Exception as e:
            raise ToolError(f"Connection failed: {e}") from e

    @classmethod
    def connect_with_factory(cls, auth_args: dict[str, Any]) -> ConnectResult:
        """Establish connection using ConIFactory based on authentication mode.

        Args:
            auth_args: Dict from ``auth_factory.resolve_auth_args_from_env()`` containing
                       ``mode`` plus all mode-specific parameters.

        Returns:
            ConnectResult with message and ConnectionInfo
        """
        mode = auth_args["mode"]
        url = auth_args["url"]
        verify_certificate = auth_args.get("verify_certificate", True)

        try:
            if mode == "basic":
                con_i = ConIFactory.basic(
                    url=url,
                    username=auth_args["username"],
                    password=auth_args["password"],
                    verify_certificate=verify_certificate,
                )
                display_username = auth_args["username"]

            elif mode == "m2m":
                con_i = ConIFactory.m2m(
                    url=url,
                    token_endpoint=auth_args["token_endpoint"],
                    client_id=auth_args["client_id"],
                    client_secret=auth_args["client_secret"],
                    scope=auth_args.get("scope"),
                    verify_certificate=verify_certificate,
                )
                display_username = auth_args["client_id"]

            elif mode == "oidc":
                con_i = ConIFactory.oidc(
                    url=url,
                    client_id=auth_args["client_id"],
                    redirect_uri=auth_args["redirect_uri"],
                    redirect_url_allow_insecure=auth_args.get("redirect_url_allow_insecure", False),
                    client_secret=auth_args.get("client_secret"),
                    scope=auth_args.get("scope"),
                    authorization_endpoint=auth_args.get("authorization_endpoint"),
                    token_endpoint=auth_args.get("token_endpoint"),
                    login_timeout=auth_args.get("login_timeout", 60),
                    verify_certificate=verify_certificate,
                    webfinger_path_prefix=auth_args.get("webfinger_path_prefix", ""),
                )
                display_username = auth_args["client_id"]

            else:
                raise ValueError(f"Unknown authentication mode: {mode!r}")

            code_example = _build_code_example(
                mode=mode,
                url=url,
                username=auth_args.get("username", ""),
                token_endpoint=auth_args.get("token_endpoint", ""),
                client_id=auth_args.get("client_id", ""),
                redirect_uri=auth_args.get("redirect_uri", ""),
            )
            return cls._init_from_con_i(
                con_i=con_i, base_url=url, display_username=display_username, code_example=code_example
            )

        except Exception as e:
            raise ToolError(f"Connection failed ({mode} mode): {e}") from e

    @classmethod
    def disconnect(cls) -> dict[str, Any]:
        """Close connection to ODS server."""
        instance = cls.get_instance()

        try:
            if instance._con_i:
                try:
                    instance._con_i.close()
                except Exception:
                    # Log but don't fail if close has issues
                    pass

            # Reset all connection state
            instance._con_i = None
            instance._model_cache = None
            instance._model = None
            instance._connection_info = None

            return {"message": "Disconnected from ODS server"}
        except Exception as e:
            raise ToolError(f"Disconnect failed: {e}") from e

    @classmethod
    def is_connected(cls) -> bool:
        """Check if connected to ODS."""
        instance = cls.get_instance()
        return instance._con_i is not None

    @classmethod
    def get_model_cache(cls) -> ModelCache | None:
        """Get ModelCache object."""
        instance = cls.get_instance()
        return instance._model_cache

    @classmethod
    def get_model(cls) -> ods.Model | None:
        """Get ODS Model object."""
        instance = cls.get_instance()
        return instance._model

    @classmethod
    def get_connection_info(cls) -> ConnectionInfo | None:
        """Get current connection information, or None if not connected."""
        instance = cls.get_instance()
        return instance._connection_info

    @classmethod
    def query(
        cls,
        jaquel_query: dict[str, Any],
        result_format: Literal["split", "records"] = "split",
        max_rows: int = 100,
        max_cells: int = 10_000,
    ) -> dict[str, Any]:
        """Execute Jaquel query on connected ODS server.

        Args:
            jaquel_query: Jaquel query as dict
            result_format: DataFrame.to_dict() orient — "split" (default) or "records".
                "split" encodes column names once; "records" repeats all keys per row.
            max_rows: Hard row cap applied before serialisation (default: 100).
            max_cells: Adaptive cell cap; effective rows = min(max_rows,
                max_cells // max(1, col_count)) (default: 10 000).

        Returns:
            Query results as dict with keys: result, total_rows, returned_rows, truncated.

        Token cost model (MCP context injection):
        -----------------------------------------
        IEEE 754 double as JSON string: worst-case ~20 chars, e.g. 3.141592653589793
        LLM tokenizers ≈ 4 chars/token  →  ~5 tokens per double value

        Example: 1 000 rows * 10 columns = 10 000 values
          Data tokens:       10 000 * 5             =  50 000 tokens  ← context-killing
          "split" overhead:  col names once          ~      50 tokens
          "records" overhead: keys * every row       ~  10 000 tokens extra

        Default caps (max_rows=100, max_cells=10_000):
          100 rows * 10 cols = 1 000 values  →  ~5 000 data tokens
          + ~20 % structure overhead          →  ~6 000 tokens total  ← safe

        Effective rows formula:
          effective_rows = min(max_rows, max_cells // max(1, col_count))
          e.g.  10 columns: min(100, 10_000 //  10) = min(100, 1000) = 100
          e.g.  50 columns: min(100, 10_000 //  50) = min(100,  200) = 100
          e.g. 200 columns: min(100, 10_000 // 200) = min(100,   50) =  50  ← auto-caps wide results
        """
        instance = cls.get_instance()

        if not instance._con_i:
            raise ToolError("Not connected to ODS server. Use 'ods_connect' tool first.")

        try:
            result = instance._con_i.query(jaquel_query, result_naming_mode="model")

            total_rows = len(result)
            col_count = len(result.columns)
            effective_rows = min(max_rows, max_cells // max(1, col_count))
            df = result.head(effective_rows)

            return {
                "result": df.to_dict(orient=result_format),
                "total_rows": total_rows,
                "returned_rows": len(df),
                "truncated": total_rows > len(df),
            }
        except Exception as e:
            raise ToolError(f"Query failed: {e}") from e
