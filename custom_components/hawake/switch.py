"""Switch platform for HaWake Alarm integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    """Set up HaWake switches."""
    coordinator = entry.runtime_data
    async_add_entities([
        HaWakeArmSwitch(coordinator),
        HaWakeAlertVibrateSwitch(coordinator),
        HaWakeAlertLoopMediaSwitch(coordinator),
    ])

    # Register factory for dynamic per-alarm switch creation
    def _switch_factory(coord: HaWakeCoordinator, alarm_index: int) -> list:
        return [HaWakePerAlarmEnabledSwitch(coord, alarm_index)]

    coordinator.register_alarm_entity_factory(_switch_factory, async_add_entities)


class HaWakeArmSwitch(CoordinatorEntity[HaWakeCoordinator], SwitchEntity):
    """Switch entity for arming/disarming the alarm system."""

    _attr_has_entity_name = True
    _attr_name = "Alarm Armed"
    _attr_icon = "mdi:shield-home"

    def __init__(self, coordinator: HaWakeCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"hawake_{coordinator.device_name}_alarm_armed"

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
        """Always available — HA is the source of truth for arm state.

        The switch can be toggled from HA even when the iOS app is offline.
        The app will pick up the retained arm/state on its next connection.
        """
        return True

    @property
    def is_on(self) -> bool:
        """Return the current arm state."""
        return self.coordinator.arm_state

    async def async_turn_on(self, **kwargs) -> None:
        """Arm — HA sets state and publishes retained to arm/state."""
        await self.coordinator.async_set_arm_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disarm — HA sets state and publishes retained to arm/state."""
        await self.coordinator.async_set_arm_state(False)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class HaWakePerAlarmEnabledSwitch(CoordinatorEntity[HaWakeCoordinator], SwitchEntity):
    """Per-alarm switch to enable/disable an individual alarm from HA."""

    _attr_has_entity_name = True
    _attr_name = "Enabled"
    _attr_icon = "mdi:alarm-check"

    def __init__(
        self, coordinator: HaWakeCoordinator, alarm_index: int
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._alarm_index = alarm_index
        self._attr_unique_id = (
            f"hawake_{coordinator.device_name}_alarm_{alarm_index}_enabled_switch"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info — grouped under the per-alarm device."""
        alarm_name = self.coordinator.get_per_alarm_state(self._alarm_index, "name")
        if alarm_name in ("Unknown", ""):
            display_name = f"HaWake {self.coordinator.device_name} - Alarm {self._alarm_index}"
        else:
            display_name = f"HaWake {self.coordinator.device_name} - {alarm_name}"
        return DeviceInfo(
            identifiers={(DOMAIN, f"hawake_{self.coordinator.device_name}_alarm_{self._alarm_index}")},
            name=display_name,
            manufacturer="HaWake",
            model="iOS Alarm Clock",
        )

    @property
    def available(self) -> bool:
        """Return True if the app is online and this alarm exists."""
        return (
            self.coordinator.app_online
            and self.coordinator.is_alarm_active(self._alarm_index)
        )

    @property
    def is_on(self) -> bool:
        """Return whether the alarm is enabled."""
        return self.coordinator.get_per_alarm_state(self._alarm_index, "enabled") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the alarm — publish MQTT command."""
        await self.coordinator.async_publish_alarm_command(
            self._alarm_index, "enabled", "ON"
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the alarm — publish MQTT command."""
        await self.coordinator.async_publish_alarm_command(
            self._alarm_index, "enabled", "OFF"
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.is_alarm_removed(self._alarm_index):
            return
        self.async_write_ha_state()


class HaWakeAlertVibrateSwitch(CoordinatorEntity[HaWakeCoordinator], SwitchEntity):
    """Switch to toggle vibration for HA alert alarms."""

    _attr_has_entity_name = True
    _attr_name = "Alert Vibrate"
    _attr_icon = "mdi:vibrate"

    def __init__(self, coordinator: HaWakeCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"hawake_{coordinator.device_name}_alert_vibrate_switch"

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

    @property
    def is_on(self) -> bool:
        """Return whether alert vibration is enabled."""
        return self.coordinator.get_dashboard_state("alert_vibrate") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Enable alert vibration."""
        await self.coordinator.async_publish_command("alert_vibrate", "ON")

    async def async_turn_off(self, **kwargs) -> None:
        """Disable alert vibration."""
        await self.coordinator.async_publish_command("alert_vibrate", "OFF")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class HaWakeAlertLoopMediaSwitch(CoordinatorEntity[HaWakeCoordinator], SwitchEntity):
    """Switch to toggle media looping for HA alert alarms."""

    _attr_has_entity_name = True
    _attr_name = "Alert Loop Media"
    _attr_icon = "mdi:repeat"

    def __init__(self, coordinator: HaWakeCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"hawake_{coordinator.device_name}_alert_loop_media_switch"

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

    @property
    def is_on(self) -> bool:
        """Return whether media looping is enabled."""
        return self.coordinator.get_dashboard_state("alert_loop_media") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Enable media looping."""
        await self.coordinator.async_publish_command("alert_loop_media", "ON")

    async def async_turn_off(self, **kwargs) -> None:
        """Disable media looping."""
        await self.coordinator.async_publish_command("alert_loop_media", "OFF")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
