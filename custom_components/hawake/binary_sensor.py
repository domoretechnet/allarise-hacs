"""Binary sensor platform for HaWake Alarm integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HaWakeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[HaWakeCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HaWake binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities([HaWakeAppOnlineSensor(coordinator)])


class HaWakeAppOnlineSensor(CoordinatorEntity[HaWakeCoordinator], BinarySensorEntity):
    """Binary sensor indicating whether the HaWake app is online."""

    _attr_has_entity_name = True
    _attr_name = "App Online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:cellphone-check"

    def __init__(self, coordinator: HaWakeCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"hawake_{coordinator.device_name}_app_online"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"hawake_{self.coordinator.device_name}_dashboard")},
            name=f"HaWake {self.coordinator.device_name} - Dashboard",
            manufacturer="HaWake",
            model="iOS Alarm Clock",
        )

    @property
    def is_on(self) -> bool:
        """Return True if the app is online."""
        return self.coordinator.app_online

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
