"""Sensors pour Nice MNCUT (informations supplémentaires).

Version: 1.0.0
Date: 2026-04-21
Changelog:
- v1.0.0: Version initiale stable avec binary sensors et alarm panel
"""

import asyncio
import logging
import time
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration des sensors via config_entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        NiceMncutStateSensor(hub, entry),
        NiceMncutAreasSensor(hub, entry),
        NiceMncutBatteryLevelSensor(hub, entry),
        NiceMncutExitDelaySensor(hub, entry),
    ]

    async_add_entities(sensors)


class NiceMncutStateSensor(SensorEntity):
    """Sensor affichant l'état brut de la centrale."""

    _attr_has_entity_name = True
    _attr_name = "État brut"
    _attr_icon = "mdi:information"

    def __init__(self, hub, entry):
        """Initialise le sensor."""
        self._hub = hub
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_raw_state"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Nice MNCUT Alarm",
            "manufacturer": "Nice",
            "model": "MNCUT",
        }

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à HA."""
        self._hub.add_listener(self._handle_hub_update)
        self._handle_hub_update()

    async def async_will_remove_from_hass(self) -> None:
        """Quand l'entité est retirée de HA."""
        self._hub.remove_listener(self._handle_hub_update)

    def _handle_hub_update(self) -> None:
        """Met à jour l'état depuis le Hub."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Retourne l'état brut."""
        return self._hub.state.get("raw_state", "unavailable")

    @property
    def available(self) -> bool:
        """Retourne True si le sensor est disponible."""
        return self._hub.available


class NiceMncutBatteryLevelSensor(SensorEntity):
    """Sensor affichant le niveau de batterie en pourcentage."""

    _attr_has_entity_name = True
    _attr_name = "Niveau batterie"
    _attr_icon = "mdi:battery"
    _attr_native_unit_of_measurement = "%"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hub, entry):
        """Initialise le sensor."""
        self._hub = hub
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_battery_level"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Nice MNCUT Alarm",
            "manufacturer": "Nice",
            "model": "MNCUT",
        }

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à HA."""
        self._hub.add_listener(self._handle_hub_update)
        self._handle_hub_update()

    async def async_will_remove_from_hass(self) -> None:
        """Quand l'entité est retirée de HA."""
        self._hub.remove_listener(self._handle_hub_update)

    def _handle_hub_update(self) -> None:
        """Met à jour l'état depuis le Hub."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int | None:
        """Retourne le niveau de batterie en %."""
        return self._hub.state.get("battery_level")

    @property
    def icon(self) -> str:
        """Icône dynamique selon le niveau."""
        level = self._hub.state.get("battery_level")
        if level is None:
            return "mdi:battery-unknown"
        elif level >= 90:
            return "mdi:battery"
        elif level >= 70:
            return "mdi:battery-80"
        elif level >= 50:
            return "mdi:battery-50"
        elif level >= 30:
            return "mdi:battery-30"
        elif level >= 10:
            return "mdi:battery-10"
        else:
            return "mdi:battery-alert"

    @property
    def available(self) -> bool:
        """Retourne True si le sensor est disponible."""
        return self._hub.available and self._hub.state.get("battery_level") is not None


class NiceMncutExitDelaySensor(SensorEntity):
    """Sensor affichant le délai de sortie restant."""

    _attr_has_entity_name = True
    _attr_name = "Délai de sortie"
    _attr_icon = "mdi:timer-sand"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(self, hub, entry):
        """Initialise le sensor."""
        self._hub = hub
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_exit_delay"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Nice MNCUT Alarm",
            "manufacturer": "Nice",
            "model": "MNCUT",
        }
        self._update_task = None

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à HA."""
        self._hub.add_listener(self._handle_hub_update)
        self._handle_hub_update()

    async def async_will_remove_from_hass(self) -> None:
        """Quand l'entité est retirée de HA."""
        self._hub.remove_listener(self._handle_hub_update)
        if self._update_task:
            self._update_task.cancel()

    def _handle_hub_update(self) -> None:
        """Met à jour l'état depuis le Hub."""
        # Si le décompte démarre, lancer une mise à jour régulière
        if self._hub.state.get("exit_delay_start") and not self._update_task:
            self._update_task = self.hass.async_create_task(self._countdown_updater())
        elif not self._hub.state.get("exit_delay_start") and self._update_task:
            self._update_task.cancel()
            self._update_task = None
        
        self.async_write_ha_state()

    async def _countdown_updater(self):
        """Met à jour le décompte toutes les secondes."""
        try:
            while self._hub.state.get("exit_delay_start"):
                await asyncio.sleep(1)
                self.async_write_ha_state()
        except asyncio.CancelledError:
            pass

    @property
    def native_value(self) -> int | None:
        """Retourne le délai restant en secondes."""
        exit_delay = self._hub.state.get("exit_delay")
        exit_delay_start = self._hub.state.get("exit_delay_start")
        
        if exit_delay and exit_delay_start:
            elapsed = time.time() - exit_delay_start
            remaining = max(0, exit_delay - int(elapsed))
            return remaining
        
        return None

    @property
    def icon(self) -> str:
        """Icône dynamique selon le temps restant."""
        remaining = self.native_value
        if remaining is None:
            return "mdi:timer-off"
        elif remaining > 5:
            return "mdi:timer-sand"
        else:
            return "mdi:timer-alert"

    @property
    def available(self) -> bool:
        """Retourne True si le sensor est disponible."""
        return self._hub.available


class NiceMncutAreasSensor(SensorEntity):
    """Sensor affichant le nombre de zones armées."""

    _attr_has_entity_name = True
    _attr_name = "Zones armées"
    _attr_icon = "mdi:home-group"

    def __init__(self, hub, entry):
        """Initialise le sensor."""
        self._hub = hub
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_zones_armees"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Nice MNCUT Alarm",
            "manufacturer": "Nice",
            "model": "MNCUT",
        }

    async def async_added_to_hass(self) -> None:
        """Quand l'entité est ajoutée à HA."""
        self._hub.add_listener(self._handle_hub_update)
        self._handle_hub_update()

    async def async_will_remove_from_hass(self) -> None:
        """Quand l'entité est retirée de HA."""
        self._hub.remove_listener(self._handle_hub_update)

    def _handle_hub_update(self) -> None:
        """Met à jour l'état depuis le Hub."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Retourne le nombre de zones armées (st=2)."""
        areas = self._hub.state.get("areas", {})
        armed_count = sum(1 for st in areas.values() if st == 2)
        return armed_count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Détails des zones."""
        areas = self._hub.state.get("areas", {})
        state_names = {
            0: "désarmée",
            1: "en cours d'armement",
            2: "armée",
            3: "alarme",
        }
        attrs = {
            f"zone_{zid}": state_names.get(st, "inconnu")
            for zid, st in areas.items()
        }
        attrs["total_zones"] = len(areas)
        attrs["zones_armees"] = sum(1 for st in areas.values() if st == 2)
        return attrs

    @property
    def available(self) -> bool:
        """Retourne True si le sensor est disponible."""
        return self._hub.available
