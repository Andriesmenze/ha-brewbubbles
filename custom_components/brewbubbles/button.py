from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import BrewBubblesClient
from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: BrewBubblesClient = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([BrewBubblesOtaButton(entry, client)])


class BrewBubblesOtaButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Start OTA Update"

    def __init__(self, entry: ConfigEntry, client: BrewBubblesClient) -> None:
        self._entry = entry
        self._client = client
        hostname = entry.data.get("hostname", entry.data["host"])
        self._attr_unique_id = f"{hostname}_ota_button"

    async def async_press(self) -> None:
        await self._client.start_ota()

    @property
    def device_info(self):
        hostname = self._entry.data.get("hostname", self._entry.data["host"])
        return {"identifiers": {(DOMAIN, hostname)}}
