"""Binary sensors pour Nice MNCUT."""

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Configuration des binary sensors via config_entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        NiceMncutBinarySensor(
            hub,
            entry,
            "battery_low",
            "Batterie faible",
            BinarySensorDeviceClass.BATTERY,
            "mdi:battery-alert",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "power_ok",
            "Alimentation secteur",
            BinarySensorDeviceClass.POWER,
            "mdi:power-plug",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "sabotage",
            "Sabotage",
            BinarySensorDeviceClass.PROBLEM,
            "mdi:shield-alert",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "contact_open",
            "Contact ouvert",
            BinarySensorDeviceClass.OPENING,
            "mdi:door-open",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "sensor_triggered",
            "Capteur déclenché",
            BinarySensorDeviceClass.MOTION,
            "mdi:motion-sensor-alert",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "panic",
            "Panique",
            BinarySensorDeviceClass.SAFETY,
            "mdi:alert-circle",
        ),
        NiceMncutBinarySensor(
            hub,
            entry,
            "maintenance",
            "Mode maintenance",
            BinarySensorDeviceClass.RUNNING,
            "mdi:wrench",
        ),
    ]

    async_add_entities(sensors)


class NiceMncutBinarySensor(BinarySensorEntity):
    """Binary sensor générique pour Nice MNCUT."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hub,
        entry,
        state_key: str,
        name: str,
        device_class: BinarySensorDeviceClass | None,
        icon: str,
    ):
        """Initialise le binary sensor."""
        self._hub = hub
        self._entry = entry
        self._state_key = state_key
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{state_key}"
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
    def is_on(self) -> bool | None:
        """Retourne True si le sensor est activé."""
        return self._hub.state.get(self._state_key, False)

    @property
    def available(self) -> bool:
        """Retourne True si le sensor est disponible."""
        return self._hub._ws is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributs supplémentaires."""
        return {
            "raw_state": self._hub.state.get("raw_state"),
        }