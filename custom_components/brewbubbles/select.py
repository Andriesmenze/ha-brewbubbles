from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import BrewBubblesClient
from .const import DOMAIN

OPT_C = "celsius"
OPT_F = "fahrenheit"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: BrewBubblesClient = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([BrewBubblesTempUnitSelect(entry, client)])


class BrewBubblesTempUnitSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Temperature Unit"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_options = [OPT_C, OPT_F]

    def __init__(self, entry: ConfigEntry, client: BrewBubblesClient) -> None:
        self._entry = entry
        self._client = client
        hostname = entry.data.get("hostname", entry.data["host"])
        self._attr_unique_id = f"{hostname}_temp_unit"

    @property
    def current_option(self) -> str | None:
        # Use the latest polled unit from /bubble/
        unit = (self.hass.data[DOMAIN][self._entry.entry_id]["coordinator"].data or {}).get("temp_unit")
        if unit == "F":
            return OPT_F
        if unit == "C":
            return OPT_C
        return None

    async def async_select_option(self, option: str) -> None:
        await self._client.set_temp_unit(option)

        # refresh bubble coordinator so unit updates in HA quickly
        coord = self.hass.data[DOMAIN][self._entry.entry_id]["coordinator"]
        await coord.async_request_refresh()

    @property
    def device_info(self):
        hostname = self._entry.data.get("hostname", self._entry.data["host"])
        return {"identifiers": {(DOMAIN, hostname)}}
