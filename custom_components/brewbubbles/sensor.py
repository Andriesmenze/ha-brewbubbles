from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BrewBubblesCoordinator

INVALID_TEMP = -100

@dataclass(frozen=True)
class BrewBubblesSensorDescription:
    key: str
    name: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None


SENSORS = [
    BrewBubblesSensorDescription(
        key="bpm",
        name="Bubbles per Minute",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrewBubblesSensorDescription(
        key="temp",
        name="Vessel Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrewBubblesSensorDescription(
        key="ambient",
        name="Ambient Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


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
    def __init__(self, coordinator: BrewBubblesCoordinator, entry: ConfigEntry, desc: BrewBubblesSensorDescription):
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = desc

        self._attr_has_entity_name = True
        self._attr_name = desc.name
        self._attr_unique_id = f"{entry.data.get('hostname', entry.data['host'])}_{desc.key}"

        if desc.device_class:
            self._attr_device_class = desc.device_class
        if desc.state_class:
            self._attr_state_class = desc.state_class

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        val = data.get(self.entity_description.key)

        if self.entity_description.key in ("temp", "ambient"):
            if val is None:
                return None
            try:
                fval = float(val)
            except (TypeError, ValueError):
                return None
            if fval == INVALID_TEMP:
                return None
            return fval

        return val

    @property
    def native_unit_of_measurement(self):
        if self.entity_description.key == "bpm":
            return "bubbles/min"

        if self.entity_description.key in ("temp", "ambient"):
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
