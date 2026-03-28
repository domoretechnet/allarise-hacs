"""Notify platform for HaWake Alarm integration.

Allows HA to call notify.send_message to trigger a full-screen alert
on the phone with a message and optional title/sound/media.
"""

from __future__ import annotations

import json
import logging

from homeassistant.components import media_source
from homeassistant.components.media_player import async_process_play_media_url
from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HaWakeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[HaWakeCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HaWake notify entity."""
    coordinator = entry.runtime_data
    async_add_entities([HaWakeNotify(coordinator)])


class HaWakeNotify(CoordinatorEntity[HaWakeCoordinator], NotifyEntity):
    """Notify entity for sending alerts to HaWake."""

    _attr_has_entity_name = True
    _attr_name = "Notify"
    _attr_icon = "mdi:bell-ring"

    def __init__(self, coordinator: HaWakeCoordinator) -> None:
        """Initialize the notify entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"hawake_{coordinator.device_name}_notify"

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
    def available(self) -> bool:
        """Return True if the app is online."""
        return self.coordinator.app_online

    async def async_send_message(self, message: str, title: str | None = None, **kwargs) -> None:
        """Send a notification — triggers a full-screen alert on the phone.

        Extra data keys supported by the iOS app:
        - sound: alert sound name
        - volume: 0-100 (defaults to the app's Media Alert Volume setting)
        - media_url: audio URL to play
        - image_url: image to display
        - video_url: video to display
        - link_url: URL to open
        """
        payload: dict = {"message": message}

        if title:
            payload["title"] = title

        # Pass through extra data
        data = kwargs.get("data") or {}
        for key in ("sound", "volume", "media_url", "image_url", "video_url", "link_url"):
            if key in data:
                payload[key] = data[key]

        # Default volume: use the app's configured Media Alert Volume if not specified.
        # The sensor stores an integer 0–100; the app's normalizeVolume() handles both
        # 0–100 integers and 0.0–1.0 floats, so we pass the raw integer.
        if "volume" not in payload:
            vol_str = self.coordinator.get_dashboard_state("media_alert_volume")
            try:
                payload["volume"] = int(vol_str)
            except (ValueError, TypeError):
                pass  # Let the app fall back to its own default

        # Sign media_url so the phone can fetch HA-hosted content
        # (e.g. TTS proxy URLs) without a Bearer token.
        if "media_url" in payload:
            url = payload["media_url"]
            if media_source.is_media_source_id(url):
                play_item = await media_source.async_resolve_media(
                    self.hass, url, self.entity_id
                )
                url = play_item.url
            payload["media_url"] = async_process_play_media_url(self.hass, url)
            _LOGGER.debug("Resolved media URL: %s", payload["media_url"])

        await self.coordinator.async_publish_command(
            "alert", json.dumps(payload)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
