"""Helpers for Sifely Open API login payloads and Authorization headers."""

from __future__ import annotations

import hashlib
import re

_SK_TOKEN_RE = re.compile(r"sk-[A-Za-z0-9_-]+")


def is_sk_token(value) -> bool:
    """Return True when value is an Open API key (sk-...)."""
    return isinstance(value, str) and value.startswith("sk-")


def md5_hex_password(plaintext: str) -> str:
    """Return the MD5 hex digest Sifely expects for login."""
    return hashlib.md5(plaintext.encode()).hexdigest()


def authorization_value(access_token) -> str:
    """Raw sk- token for Open API; Bearer prefix only for legacy tokens."""
    return access_token if str(access_token).startswith("sk-") else f"Bearer {access_token}"


def parse_login_payload(resp_json):
    """
    Accept both Open API login shapes and return the token-bearing dict.

    a) {"code": 200, "data": {"clientToken": "sk-...", "clientId": "cli_...", ...}}
    b) {"clientToken": "sk-...", "clientId": "cli_...", "account": "...", "plan": "DEVELOPER", ...}
    """
    if not isinstance(resp_json, dict):
        raise ValueError(f"Login failed: unexpected payload {resp_json!r}")

    data = resp_json
    if isinstance(resp_json.get("data"), dict):
        if resp_json.get("code") not in (None, 200):
            raise ValueError(f"Login failed: {resp_json}")
        data = resp_json["data"]
    elif resp_json.get("code") not in (None, 200):
        raise ValueError(f"Login failed: {resp_json}")

    token = data.get("clientToken") or data.get("token")
    if not token:
        raise ValueError(f"Login failed: missing token in {resp_json}")
    return data


def extract_access_token(data: dict):
    """Token = data.clientToken or data.token."""
    return data.get("clientToken") or data.get("token")


def extract_client_id(data: dict):
    """Config-flow client_id: prefer clientToken, else clientId."""
    return data.get("clientToken") or data.get("clientId")


def redact_secrets(text: str) -> str:
    """Strip sk- tokens from log snippets. Never log passwords."""
    if not text:
        return text
    return _SK_TOKEN_RE.sub("sk-[REDACTED]", text)
