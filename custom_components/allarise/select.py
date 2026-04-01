"""Select platform for Allarise Alarm — sleep sound selector."""
from __future__ import annotations

import json
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AllariseCoordinator

_LOGGER = logging.getLogger(__name__)

# Must match the filenames (without .m4a) bundled in the iOS app's Sleep Sounds folder.
# "none" represents stopped / no sound playing.
SLEEP_SOUND_OPTIONS = [
    "none",
    "Brown_Noise",
    "Fan",
    "Light_Rain",
    "Mountain_Stream",
    "Summer_Rain",
    "white_noise",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Allarise select entities."""
    coordinator: AllariseCoordinator = entry.runtime_data
    async_add_entities([SleepSoundSelectEntity(coordinator)])


class SleepSoundSelectEntity(SelectEntity):
    """Dropdown to start/change/stop the sleep sound playing on the iOS device."""

    _attr_has_entity_name = True
    _attr_name = "Sleep Sound"
    _attr_icon = "mdi:music-note-bluetooth"
    _attr_options = SLEEP_SOUND_OPTIONS

    def __init__(self, coordinator: AllariseCoordinator) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"allarise_{coordinator.device_name}_sleep_sound_select"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"allarise_{coordinator.device_name}_dashboard")},
        }

    @property
    def available(self) -> bool:
        return self._coordinator.app_online

    @property
    def current_option(self) -> str:
        val = self._coordinator.get_dashboard_state("sleep_sound")
        return val if val in SLEEP_SOUND_OPTIONS else "none"

    async def async_select_option(self, option: str) -> None:
        if option == "none":
            await self._coordinator.async_publish_command("sleep_sound_stop")
        else:
            payload = json.dumps({"sound": option})
            await self._coordinator.async_publish_command("sleep_sound_start", payload)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
