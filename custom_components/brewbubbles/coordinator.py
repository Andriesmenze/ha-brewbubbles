from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BrewBubblesClient, BrewBubblesApiError

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

class BrewBubblesCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, client: BrewBubblesClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Brew Bubbles",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            return await self.client.get_bubble()
        except BrewBubblesApiError as err:
            raise UpdateFailed(str(err)) from err
