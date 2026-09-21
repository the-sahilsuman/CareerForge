from typing import Any

import httpx
from jose import JWTError, jwt

from app.core.config import settings


class CognitoJWTError(Exception):
    """Raised when a Cognito JWT cannot be trusted."""


_jwks_cache: dict[str, Any] | None = None


def _get_jwks() -> dict[str, Any]:
    global _jwks_cache

    if _jwks_cache is not None:
        return _jwks_cache

    try:
        response = httpx.get(
            settings.cognito_jwks_url,
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise CognitoJWTError(
            "Unable to fetch Cognito signing keys."
        ) from exc

    _jwks_cache = response.json()

    return _jwks_cache


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise CognitoJWTError(
            "Invalid JWT header."
        ) from exc

    kid = unverified_header.get("kid")

    if not kid:
        raise CognitoJWTError(
            "JWT does not contain a key ID."
        )

    jwks = _get_jwks()

    key = next(
        (
            key
            for key in jwks.get("keys", [])
            if key.get("kid") == kid
        ),
        None,
    )

    if key is None:
        # Signing keys can rotate. Refresh once.
        global _jwks_cache
        _jwks_cache = None

        jwks = _get_jwks()

        key = next(
            (
                key
                for key in jwks.get("keys", [])
                if key.get("kid") == kid
            ),
            None,
        )

    if key is None:
        raise CognitoJWTError(
            "Unable to find JWT signing key."
        )

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=settings.cognito_issuer,
            options={
                "verify_aud": False,
            },
        )
    except JWTError as exc:
        raise CognitoJWTError(
            "JWT signature or claims validation failed."
        ) from exc

    if payload.get("token_use") != "access":
        raise CognitoJWTError(
            "Expected a Cognito access token."
        )

    if payload.get("client_id") != settings.cognito_client_id:
        raise CognitoJWTError(
            "Token was issued for an unexpected client."
        )

    if not payload.get("sub"):
        raise CognitoJWTError(
            "Token does not contain a subject."
        )

    return payload