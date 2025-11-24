"""ODS Connection Manager for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any

try:
    from odsbox import ConI
    from odsbox.model_cache import ModelCache
    from odsbox.proto import ods

    ODSBOX_AVAILABLE = True
except ImportError:
    ODSBOX_AVAILABLE = False


class ODSConnectionManager:
    """Manages connection to ASAM ODS server and provides model access."""

    _instance: ODSConnectionManager | None = None
    _con_i: ConI | None = None
    _model_cache: ModelCache | None = None
    _model: ods.Model | None = None
    _connection_info: dict[str, Any] = {}

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
    def connect(cls, url: str, auth: tuple, **kwargs) -> dict[str, Any]:
        """Establish connection to ODS server.

        Args:
            url: ODS API URL (e.g., http://localhost:8087/api)
            auth: (username, password) tuple
            **kwargs: Additional ConI parameters

        Returns:
            Connection status dict
        """
        if not ODSBOX_AVAILABLE:
            return {"success": False, "error": "odsbox not installed", "hint": "Install odsbox: pip install odsbox"}

        try:
            instance = cls.get_instance()
            # Close existing connection if any
            if instance._con_i:
                try:
                    instance._con_i.close()
                except Exception:
                    pass

            # Establish new connection
            instance._con_i = ConI(url=url, auth=auth, load_model=True, **kwargs)

            # Load model
            instance._model_cache = instance._con_i.mc
            instance._model = instance._con_i.model()

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

            instance._connection_info = {
                "url": url,
                "username": auth[0] if isinstance(auth, tuple) else "unknown",
                "con_i_url": instance._con_i.con_i_url(),
                "status": "connected",
                "available_entities": list(instance._model.entities.keys()) if instance._model else [],
                "initial_query": initial_query,
            }

            return {"success": True, "message": "Connected to ODS server", "connection": instance._connection_info}

        except Exception as e:
            return {"success": False, "error": str(e), "error_type": type(e).__name__}

    @classmethod
    def disconnect(cls) -> dict[str, Any]:
        """Close connection to ODS server."""
        instance = cls.get_instance()

        try:
            if instance._con_i:
                try:
                    instance._con_i.close()
                except Exception as close_err:
                    # Log but don't fail if close has issues
                    pass
            
            # Reset all connection state
            instance._con_i = None
            instance._model_cache = None
            instance._model = None
            instance._connection_info = {}

            return {"success": True, "message": "Disconnected from ODS server"}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
    def get_connection_info(cls) -> dict[str, Any]:
        """Get current connection information."""
        instance = cls.get_instance()
        return instance._connection_info.copy()

    @classmethod
    def query(cls, jaquel_query: dict) -> dict[str, Any]:
        """Execute Jaquel query on connected ODS server.

        Args:
            jaquel_query: Jaquel query as dict

        Returns:
            Query results as dict/DataFrame compatible format
        """
        instance = cls.get_instance()

        if not instance._con_i:
            return {"error": "Not connected to ODS server", "hint": "Use 'connect_ods_server' tool first"}

        try:
            result = instance._con_i.query_data(jaquel_query)
            entity_count = len(result.dataMatrices) if hasattr(result, "dataMatrices") else 0
            return {"success": True, "result": result, "entity_count": entity_count}
        except Exception as e:
            return {"error": str(e), "error_type": type(e).__name__, "query": jaquel_query}
