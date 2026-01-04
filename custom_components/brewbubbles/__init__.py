from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .api import BrewBubblesClient
from .const import DOMAIN
from .coordinator import BrewBubblesCoordinator, BrewBubblesVersionCoordinator

PLATFORMS = ["sensor", "button", "update"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = BrewBubblesClient(session, entry.data["host"])

    coordinator = BrewBubblesCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    version_coordinator = BrewBubblesVersionCoordinator(hass, client)
    await version_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
        "version_coordinator": version_coordinator,
    }

    # Register device with a stable identifier (hostname), but a friendly name (fermenter name)
    hostname = entry.data.get("hostname", entry.data["host"])
    fermenter_name = (coordinator.data or {}).get("name") or entry.title or hostname

    device_reg = dr.async_get(hass)
    device_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, hostname)},
        name=fermenter_name,
        manufacturer="Brew Bubbles",
        model="Brew Bubbles",
        configuration_url=f"http://{entry.data['host']}",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
