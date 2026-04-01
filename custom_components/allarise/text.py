"""Text platform for Allarise Alarm integration."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TEXT_ENTITIES
from .coordinator import AllariseCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[AllariseCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Allarise text entities."""
    coordinator = entry.runtime_data
    entities: list[TextEntity] = []

    for key, name_suffix, icon in TEXT_ENTITIES:
        entities.append(
            AllariseTextEntity(coordinator, key, name_suffix, icon)
        )

    async_add_entities(entities)


class AllariseTextEntity(CoordinatorEntity[AllariseCoordinator], TextEntity):
    """A text entity for sending commands to Allarise (alert, create/update/delete alarm)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_max = 65535

    def __init__(
        self,
        coordinator: AllariseCoordinator,
        key: str,
        name_suffix: str,
        icon: str,
    ) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name_suffix
        self._attr_icon = icon
        self._attr_unique_id = f"allarise_{coordinator.device_name}_{key}"
        self._attr_native_value = ""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"allarise_{self.coordinator.device_name}_dashboard")},
            name=f"Allarise {self.coordinator.device_name} - Dashboard",
            manufacturer="Allarise",
            model="iOS Alarm Clock",
        )

    @property
    def available(self) -> bool:
        """Return True if the app is online."""
        return self.coordinator.app_online

    async def async_set_value(self, value: str) -> None:
        """Handle the text being set — publish MQTT command."""
        self._attr_native_value = value
        await self.coordinator.async_publish_command(self._key, value)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
