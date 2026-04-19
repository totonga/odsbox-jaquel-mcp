"""Authentication factory for resolving ODS connection parameters from environment variables.

Supports three authentication modes via ConIFactory:
- basic: Username/password authentication (default, backward compatible)
- m2m: Machine-to-machine OAuth2 client credentials
- oidc: OpenID Connect interactive browser login

Secrets (passwords, client_secrets) fall back to keyring lookup when not
found in environment variables.
"""

from __future__ import annotations

import logging
import os
from typing import Any, cast

logger = logging.getLogger(__name__)

VALID_MODES = ("basic", "m2m", "oidc")


def _get_secret_from_keyring(service: str, username: str) -> str | None:
    """Retrieve a secret from keyring, returning None if unavailable.

    Args:
        service: Keyring service name (typically the URL or token endpoint).
        username: Keyring username (typically the user or client_id).

    Returns:
        The secret string, or None if keyring is not installed or the secret is not found.
    """
    try:
        import keyring

        return cast(str | None, keyring.get_password(service, username))
    except Exception:
        return None


def _env_get(env: os._Environ, prefix: str, key: str) -> str | None:  # type: ignore[type-arg]
    """Look up an environment variable with prefix fallback to ODS_ legacy prefix."""
    return env.get(f"{prefix}_{key}") or env.get(f"ODS_{key}")


def _parse_verify(env: os._Environ, prefix: str) -> bool:  # type: ignore[type-arg]
    """Parse the VERIFY environment variable as a boolean."""
    verify_str = _env_get(env, prefix, "VERIFY")
    if verify_str is None or str(verify_str).strip() == "":
        return True
    return str(verify_str).strip().lower() in ("1", "true", "yes", "y")


def _require_url(env: os._Environ, prefix: str) -> str:  # type: ignore[type-arg]
    """Resolve and validate the ODS server URL from environment."""
    url = _env_get(env, prefix, "URL") or _env_get(env, prefix, "API_URL")
    if not url or not isinstance(url, str) or not url.strip():
        raise ValueError(f"Environment variable {prefix}_URL (or {prefix}_API_URL) must be set to a non-empty string")
    return url.strip()


def _resolve_basic_auth(env: os._Environ, prefix: str) -> dict[str, Any]:  # type: ignore[type-arg]
    """Resolve basic authentication parameters from environment.

    Falls back to keyring for password if not found in environment.
    """
    url = _require_url(env, prefix)

    username = _env_get(env, prefix, "USERNAME") or _env_get(env, prefix, "USER")
    if not username or not isinstance(username, str) or not username.strip():
        raise ValueError(
            f"Environment variable {prefix}_USERNAME (or {prefix}_USER) must be set to a non-empty string"
        )
    username = username.strip()

    password = _env_get(env, prefix, "PASSWORD") or _env_get(env, prefix, "PWD")
    if not password or not isinstance(password, str) or not password.strip():
        # Keyring fallback
        password = _get_secret_from_keyring(url, username)
        if not password:
            raise ValueError(
                f"Password not found. Set {prefix}_PASSWORD (or {prefix}_PWD) "
                f"or store it in keyring:\n"
                f"  keyring set '{url}' '{username}'"
            )
    else:
        password = password.strip()

    return {
        "mode": "basic",
        "url": url,
        "username": username,
        "password": password,
        "verify_certificate": _parse_verify(env, prefix),
    }


def _resolve_m2m_auth(env: os._Environ, prefix: str) -> dict[str, Any]:  # type: ignore[type-arg]
    """Resolve M2M (machine-to-machine) authentication parameters from environment.

    Falls back to keyring for client_secret if not found in environment.
    """
    url = _require_url(env, prefix)

    token_endpoint = _env_get(env, prefix, "M2M_TOKEN_ENDPOINT")
    if not token_endpoint or not isinstance(token_endpoint, str) or not token_endpoint.strip():
        raise ValueError(
            f"Environment variable {prefix}_M2M_TOKEN_ENDPOINT must be set for M2M mode "
            "(e.g., https://auth.example.com/realms/myrealm/protocol/openid-connect/token)"
        )
    token_endpoint = token_endpoint.strip()

    client_id = _env_get(env, prefix, "M2M_CLIENT_ID")
    if not client_id or not isinstance(client_id, str) or not client_id.strip():
        raise ValueError(f"Environment variable {prefix}_M2M_CLIENT_ID must be set for M2M mode")
    client_id = client_id.strip()

    client_secret = _env_get(env, prefix, "M2M_CLIENT_SECRET")
    if not client_secret or not isinstance(client_secret, str) or not client_secret.strip():
        # Keyring fallback
        client_secret = _get_secret_from_keyring(token_endpoint, client_id)
        if not client_secret:
            raise ValueError(
                f"Client secret not found. Set {prefix}_M2M_CLIENT_SECRET "
                f"or store it in keyring:\n"
                f"  keyring set '{token_endpoint}' '{client_id}'"
            )
    else:
        client_secret = client_secret.strip()

    # Scope is optional, comma-separated
    scope_str = _env_get(env, prefix, "M2M_SCOPE")
    scope: list[str] | None = None
    if scope_str and scope_str.strip():
        scope = [s.strip() for s in scope_str.split(",") if s.strip()]

    return {
        "mode": "m2m",
        "url": url,
        "token_endpoint": token_endpoint,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "verify_certificate": _parse_verify(env, prefix),
    }


def _resolve_oidc_auth(env: os._Environ, prefix: str) -> dict[str, Any]:  # type: ignore[type-arg]
    """Resolve OIDC authentication parameters from environment.

    client_secret is optional (public clients do not require one).
    Falls back to keyring for client_secret if not found in environment.
    """
    url = _require_url(env, prefix)

    client_id = _env_get(env, prefix, "OIDC_CLIENT_ID")
    if not client_id or not isinstance(client_id, str) or not client_id.strip():
        raise ValueError(f"Environment variable {prefix}_OIDC_CLIENT_ID must be set for OIDC mode")
    client_id = client_id.strip()

    redirect_uri = _env_get(env, prefix, "OIDC_REDIRECT_URI")
    if not redirect_uri or not isinstance(redirect_uri, str) or not redirect_uri.strip():
        raise ValueError(
            f"Environment variable {prefix}_OIDC_REDIRECT_URI must be set for OIDC mode (e.g., http://127.0.0.1:1234)"
        )
    redirect_uri = redirect_uri.strip()

    # Optional: client_secret (public clients may not need this)
    client_secret = _env_get(env, prefix, "OIDC_CLIENT_SECRET")
    if client_secret and isinstance(client_secret, str) and client_secret.strip():
        client_secret = client_secret.strip()
    else:
        # Try keyring, but don't fail if not found (public client)
        client_secret = _get_secret_from_keyring(url, client_id)
        # client_secret may still be None — that's OK for public clients

    # Optional: allow insecure redirect (HTTP instead of HTTPS)
    redirect_insecure_str = _env_get(env, prefix, "OIDC_REDIRECT_INSECURE")
    redirect_url_allow_insecure = False
    if redirect_insecure_str and str(redirect_insecure_str).strip():
        redirect_url_allow_insecure = str(redirect_insecure_str).strip().lower() in ("1", "true", "yes", "y")

    # Optional: WebFinger path prefix
    webfinger_path_prefix = _env_get(env, prefix, "OIDC_WEBFINGER_PATH_PREFIX") or ""

    # Optional: explicit endpoints (skip WebFinger discovery)
    authorization_endpoint = _env_get(env, prefix, "OIDC_AUTHORIZATION_ENDPOINT")
    if authorization_endpoint:
        authorization_endpoint = authorization_endpoint.strip() or None

    token_endpoint = _env_get(env, prefix, "OIDC_TOKEN_ENDPOINT")
    if token_endpoint:
        token_endpoint = token_endpoint.strip() or None

    # Optional: login timeout
    login_timeout = 60
    login_timeout_str = _env_get(env, prefix, "OIDC_LOGIN_TIMEOUT")
    if login_timeout_str and login_timeout_str.strip():
        try:
            login_timeout = int(login_timeout_str.strip())
        except ValueError:
            raise ValueError(
                f"Environment variable {prefix}_OIDC_LOGIN_TIMEOUT must be an integer, got: {login_timeout_str!r}"
            )

    # Optional: scope
    scope_str = _env_get(env, prefix, "OIDC_SCOPE")
    scope: list[str] | None = None
    if scope_str and scope_str.strip():
        scope = [s.strip() for s in scope_str.split(",") if s.strip()]

    return {
        "mode": "oidc",
        "url": url,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "redirect_url_allow_insecure": redirect_url_allow_insecure,
        "client_secret": client_secret,
        "scope": scope,
        "authorization_endpoint": authorization_endpoint,
        "token_endpoint": token_endpoint,
        "login_timeout": login_timeout,
        "verify_certificate": _parse_verify(env, prefix),
        "webfinger_path_prefix": webfinger_path_prefix,
    }


def resolve_auth_args_from_env(prefix: str) -> dict[str, Any]:
    """Resolve authentication arguments from environment variables.

    Detects the authentication mode from ``{prefix}_MODE`` (or ``ODS_MODE``),
    defaulting to ``"basic"`` for backward compatibility.

    Returns a dict with ``"mode"`` plus all mode-specific parameters needed
    by ``ODSConnectionManager.connect_with_factory()``.

    Raises:
        ValueError: If required variables are missing or mode is invalid.
    """
    env = os.environ

    mode_str = _env_get(env, prefix, "MODE")
    mode = mode_str.strip().lower() if mode_str and mode_str.strip() else "basic"

    if mode not in VALID_MODES:
        raise ValueError(
            f"Invalid authentication mode: {mode!r}. Set {prefix}_MODE to one of: {', '.join(VALID_MODES)}"
        )

    if mode == "basic":
        return _resolve_basic_auth(env, prefix)
    elif mode == "m2m":
        return _resolve_m2m_auth(env, prefix)
    elif mode == "oidc":
        return _resolve_oidc_auth(env, prefix)
    else:
        raise ValueError(
            f"Unhandled authentication mode: {mode!r}. Set {prefix}_MODE to one of: {', '.join(VALID_MODES)}"
        )
