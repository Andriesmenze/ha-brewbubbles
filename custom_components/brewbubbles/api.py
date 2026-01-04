from __future__ import annotations

import async_timeout
from aiohttp import ClientSession

class BrewBubblesApiError(Exception):
    """Base error."""

class BrewBubblesCannotConnect(BrewBubblesApiError):
    """Connection error."""

class BrewBubblesInvalidResponse(BrewBubblesApiError):
    """Unexpected response / not a Brew Bubbles device."""


class BrewBubblesClient:
    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self._host = host.rstrip("/")

    def _url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"http://{self._host}{path}"

    async def get_config(self) -> dict:
        return await self._get_json("/config/")

    async def get_bubble(self) -> dict:
        return await self._get_json("/bubble/")

    async def get_this_version(self) -> dict:
        return await self._get_json("/thisVersion/")

    async def _get_json(self, path: str) -> dict:
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(self._url(path))
            resp.raise_for_status()
            data = await resp.json(content_type=None)
        except Exception as err:
            raise BrewBubblesCannotConnect(str(err)) from err

        if not isinstance(data, dict):
            raise BrewBubblesInvalidResponse("Expected JSON object")
        return data
