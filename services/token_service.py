"""Token retrieval and caching for YonBIP APIs."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

import requests

from . import config


@dataclass
class CachedToken:
    token: str
    expires_at: float


class TokenService:
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._cache: Optional[CachedToken] = None
        self._last_expire: int = 7200

    def get_token(self, *, force_refresh: bool = False) -> str:
        with self._lock:
            now = time.time()
            if (
                not force_refresh
                and self._cache
                and self._cache.expires_at > now
            ):
                return self._cache.token

            token = self._fetch_token()
            expires_at = time.time() + max(self._last_expire - 60, 60)
            self._cache = CachedToken(token=token, expires_at=expires_at)
            return token

    def _fetch_token(self) -> str:
        timestamp = str(int(time.time() * 1000))
        params = {"appKey": config.APP_KEY, "timestamp": timestamp}
        signature = self._build_signature(params, config.APP_SECRET)
        params["signature"] = signature

        url = config.TOKEN_URL.rstrip("/") + config.SELF_APP_TOKEN_PATH
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "00000":
            raise RuntimeError(f"Failed to fetch token: {data}")
        token_data = data.get("data", {})
        token = token_data.get("access_token")
        if not token:
            raise RuntimeError("Token missing in response")
        self._last_expire = int(token_data.get("expire", 7200))
        return token

    @staticmethod
    def _build_signature(params: dict[str, str], secret: str) -> str:
        to_sign = f"appKey{params.get('appKey', '')}timestamp{params.get('timestamp', '')}"
        return TokenService._hmac_sha256(secret, to_sign)

    @staticmethod
    def _hmac_sha256(secret: str, message: str) -> str:
        import base64
        import hashlib
        import hmac

        digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")


TOKEN_SERVICE = TokenService()
