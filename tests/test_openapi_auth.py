"""Unit tests for Open API login parsing and Authorization headers.

These tests do not call Sifely and do not use real credentials.
"""

from __future__ import annotations

import hashlib
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPONENT = os.path.join(ROOT, "custom_components", "sifely_cloud")


def _load(name: str, filename: str):
    import importlib.util

    path = os.path.join(COMPONENT, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


const = _load("sifely_const", "const.py")
auth = _load("sifely_openapi_auth", "openapi_auth.py")
API_BASE_URL = const.API_BASE_URL
DOMAIN = const.DOMAIN
LOGIN_ENDPOINT = const.LOGIN_ENDPOINT
REFRESH_ENDPOINT = const.REFRESH_ENDPOINT
TOKEN_ENDPOINT = const.TOKEN_ENDPOINT
VERSION = const.VERSION
authorization_value = auth.authorization_value
extract_access_token = auth.extract_access_token
extract_client_id = auth.extract_client_id
is_sk_token = auth.is_sk_token
md5_hex_password = auth.md5_hex_password
parse_login_payload = auth.parse_login_payload
redact_secrets = auth.redact_secrets


class ConstTests(unittest.TestCase):
    def test_domain_unchanged(self):
        self.assertEqual(DOMAIN, "sifely_cloud")

    def test_version_bumped(self):
        self.assertEqual(VERSION, "1.3.0")

    def test_openapi_base_and_derived_endpoints(self):
        self.assertEqual(API_BASE_URL, "https://cus-openapi.sifely.com")
        self.assertEqual(TOKEN_ENDPOINT, "https://cus-openapi.sifely.com/system/smart/login")
        self.assertEqual(LOGIN_ENDPOINT, "https://cus-openapi.sifely.com/system/smart/loginByGuest")
        self.assertEqual(REFRESH_ENDPOINT, "https://cus-openapi.sifely.com/system/smart/oauthToken")
        self.assertTrue(TOKEN_ENDPOINT.startswith(API_BASE_URL))
        self.assertNotIn("app-smart-server.sifely.com", API_BASE_URL)


class LoginParseTests(unittest.TestCase):
    def test_wrapped_code_200_data(self):
        payload = {
            "code": 200,
            "data": {
                "clientToken": "sk-unit-test-token",
                "clientId": "cli_unit_test",
                "plan": "DEVELOPER",
            },
        }
        data = parse_login_payload(payload)
        self.assertEqual(extract_access_token(data), "sk-unit-test-token")
        self.assertEqual(extract_client_id(data), "sk-unit-test-token")

    def test_unwrapped_production_shape(self):
        payload = {
            "clientToken": "sk-unit-test-token",
            "clientId": "cli_unit_test",
            "account": "unit-test-account",
            "plan": "DEVELOPER",
        }
        data = parse_login_payload(payload)
        self.assertEqual(extract_access_token(data), "sk-unit-test-token")
        self.assertEqual(extract_client_id(data), "sk-unit-test-token")
        self.assertEqual(data.get("clientId"), "cli_unit_test")

    def test_legacy_token_field(self):
        payload = {"code": 200, "data": {"token": "legacy-oauth-token", "refreshToken": "r1"}}
        data = parse_login_payload(payload)
        self.assertEqual(extract_access_token(data), "legacy-oauth-token")

    def test_wrapped_error_code_raises(self):
        with self.assertRaises(ValueError):
            parse_login_payload({"code": 401, "data": {"msg": "nope"}})

    def test_missing_token_raises(self):
        with self.assertRaises(ValueError):
            parse_login_payload({"plan": "DEVELOPER"})


class AuthHeaderTests(unittest.TestCase):
    def test_sk_token_is_raw(self):
        self.assertEqual(authorization_value("sk-unit-test-token"), "sk-unit-test-token")
        self.assertTrue(is_sk_token("sk-abc"))

    def test_legacy_token_gets_bearer(self):
        self.assertEqual(authorization_value("legacy-oauth-token"), "Bearer legacy-oauth-token")
        self.assertFalse(is_sk_token("legacy-oauth-token"))

    def test_md5_hex_password(self):
        self.assertEqual(md5_hex_password("secret"), hashlib.md5(b"secret").hexdigest())

    def test_redact_sk_tokens(self):
        text = redact_secrets("got sk-unit-test-token from api")
        self.assertNotIn("sk-unit-test-token", text)
        self.assertIn("sk-[REDACTED]", text)


if __name__ == "__main__":
    unittest.main()
