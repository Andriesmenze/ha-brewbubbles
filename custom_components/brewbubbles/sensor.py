from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BrewBubblesCoordinator

INVALID_TEMP = -100.0


SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="bpm",
        name="Bubbles per Minute",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="temp",
        name="Vessel Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="ambient",
        name="Ambient Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BrewBubblesCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        BrewBubblesSensor(coordinator, entry, desc)
        for desc in SENSORS
    )


class BrewBubblesSensor(CoordinatorEntity[BrewBubblesCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BrewBubblesCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry

        hostname = entry.data.get("hostname", entry.data["host"])
        self._attr_unique_id = f"{hostname}_{description.key}"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        key = self.entity_description.key
        val = data.get(key)

        if key == "bpm":
            val = data.get("bpm")
            if val is None:
                return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        if key in ("temp", "ambient"):
            if val is None:
                return None
            try:
                fval = float(val)
            except (TypeError, ValueError):
                return None

            if fval <= -127:
                return None

            return fval
        
        return data.get(key)

    @property
    def native_unit_of_measurement(self):
        key = self.entity_description.key

        if key == "bpm":
            return "bubbles/min"

        if key in ("temp", "ambient"):
            unit = (self.coordinator.data or {}).get("temp_unit")
            if unit == "F":
                return UnitOfTemperature.FAHRENHEIT
            return UnitOfTemperature.CELSIUS

        return None

    @property
    def device_info(self):
        hostname = self._entry.data.get("hostname", self._entry.data["host"])
        return {
            "identifiers": {(DOMAIN, hostname)},
            "name": f"Brew Bubbles ({hostname})",
            "manufacturer": "Brew Bubbles",
            "configuration_url": f"http://{self._entry.data['host']}",
        }
