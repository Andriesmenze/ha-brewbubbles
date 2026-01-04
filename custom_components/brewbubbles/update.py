from __future__ import annotations

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import BrewBubblesClient
from .const import DOMAIN
from .coordinator import BrewBubblesVersionCoordinator

def _ver_str(v: dict | None) -> str | None:
    if not isinstance(v, dict):
        return None
    return v.get("version")

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: BrewBubblesClient = hass.data[DOMAIN][entry.entry_id]["client"]
    vcoord: BrewBubblesVersionCoordinator = hass.data[DOMAIN][entry.entry_id]["version_coordinator"]
    async_add_entities([BrewBubblesFirmwareUpdate(entry, client, vcoord)])


class BrewBubblesFirmwareUpdate(CoordinatorEntity[BrewBubblesVersionCoordinator], UpdateEntity):
    _attr_has_entity_name = True
    _attr_name = "Firmware"
    _attr_title = "Brew Bubbles Firmware"

    def __init__(
        self,
        entry: ConfigEntry,
        client: BrewBubblesClient,
        coordinator: BrewBubblesVersionCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._client = client
        hostname = entry.data.get("hostname", entry.data["host"])
        self._attr_unique_id = f"{hostname}_firmware_update"

    @property
    def installed_version(self) -> str | None:
        data = self.coordinator.data or {}
        return _ver_str(data.get("this"))

    @property
    def latest_version(self) -> str | None:
        data = self.coordinator.data or {}
        return _ver_str(data.get("that"))

    @property
    def update_available(self) -> bool:
        iv = self.installed_version
        lv = self.latest_version
        return bool(iv and lv and iv != lv)

    async def async_install(self, version: str | None, backup: bool, **kwargs) -> None:
        # Trigger device OTA; Brew Bubbles handles download + flash
        await self._client.start_ota()

    @property
    def device_info(self):
        hostname = self._entry.data.get("hostname", self._entry.data["host"])
        return {"identifiers": {(DOMAIN, hostname)}}
