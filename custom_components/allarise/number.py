"""Number platform for Allarise Alarm integration — Sleep Sound volume slider."""

from __future__ import annotations

import json

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AllariseCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[AllariseCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Allarise number entities."""
    coordinator = entry.runtime_data
    async_add_entities([AllariseSleepSoundVolumeNumber(coordinator)])


class AllariseSleepSoundVolumeNumber(CoordinatorEntity[AllariseCoordinator], NumberEntity):
    """Volume slider for the active Sleep Sound session (0–100)."""

    _attr_has_entity_name = True
    _attr_name = "Sleep Volume"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: AllariseCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"allarise_{coordinator.device_name}_sleep_sound_volume"

    @property
    def device_info(self) -> DeviceInfo:
        """Group under the Dashboard device."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"allarise_{self.coordinator.device_name}_dashboard")},
            name=f"Allarise {self.coordinator.device_name} - Dashboard",
            manufacturer="Allarise",
            model="iOS Alarm Clock",
        )

    @property
    def available(self) -> bool:
        """Available whenever the app is online."""
        return self.coordinator.app_online

    @property
    def native_value(self) -> float | None:
        """Return the current sleep sound volume (0–100), or None if unknown."""
        raw = self.coordinator.get_dashboard_state("sleep_sound_volume")
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Publish a sleep_sound_set_volume command to the iOS app."""
        payload = json.dumps({"volume": int(value)})
        await self.coordinator.async_publish_command("sleep_sound_set_volume", payload)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
