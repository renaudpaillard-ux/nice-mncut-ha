"""Plateforme Alarm Control Panel pour Nice MNCUT."""

import logging
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Mapping états Nice → États HA (sans triggered)
STATE_MAP = {
    "armed_away": AlarmControlPanelState.ARMED_AWAY,
    "armed_home": AlarmControlPanelState.ARMED_HOME,
    "arming": AlarmControlPanelState.ARMING,
    "disarmed": AlarmControlPanelState.DISARMED,
    "disarming": AlarmControlPanelState.DISARMING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration de l'alarme via config_entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NiceMncutAlarmPanel(hub, entry)])


class NiceMncutAlarmPanel(AlarmControlPanelEntity):
    """Panneau d'alarme Nice MNCUT."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )
    _attr_code_arm_required = False

    def __init__(self, hub, entry):
        """Initialise le panneau d'alarme."""
        self._hub = hub
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_alarm_panel"
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
    def available(self) -> bool:
        """Retourne True si l'entité est disponible."""
        return self._hub.available

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Retourne l'état actuel de l'alarme."""
        hub_state = self._hub.state.get("armed_status")
        return STATE_MAP.get(hub_state)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Attributs supplémentaires."""
        return {
            "raw_state": self._hub.state.get("raw_state"),
            "areas": self._hub.state.get("areas", {}),
            "battery_low": self._hub.state.get("battery_low", False),
            "power_ok": self._hub.state.get("power_ok", True),
            "sabotage": self._hub.state.get("sabotage", False),
            "contact_open": self._hub.state.get("contact_open", False),
            "panic": self._hub.state.get("panic", False),
        }

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Désarme l'alarme."""
        if self._can_disarm():
            await self._hub.send_command("C00102")
        else:
            _LOGGER.warning("Désarmement bloqué par l'état actuel")

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arme en mode partiel (présence)."""
        if self._can_arm():
            await self._hub.send_command("C00103", "123---")
        else:
            _LOGGER.warning("Armement partiel bloqué: vérifier les conditions")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arme en mode total (absence)."""
        if self._can_arm():
            await self._hub.send_command("C00101")
        else:
            _LOGGER.warning("Armement total bloqué: vérifier les conditions")

    def _can_arm(self) -> bool:
        """Vérifie si l'armement est possible."""
        # Bloque si sabotage ou contact ouvert
        if self._hub.state.get("sabotage", False):
            _LOGGER.error("Armement impossible: sabotage détecté")
            return False

        if self._hub.state.get("contact_open", False):
            _LOGGER.error("Armement impossible: contact ouvert")
            return False

        # Batterie faible ou coupure secteur = warning mais on permet
        if self._hub.state.get("battery_low", False):
            _LOGGER.warning("Armement avec batterie faible")

        if not self._hub.state.get("power_ok", True):
            _LOGGER.warning("Armement avec coupure secteur")

        return True

    def _can_disarm(self) -> bool:
        """Vérifie si le désarmement est possible."""
        # Le désarmement est toujours possible sauf en cas de panique
        if self._hub.state.get("panic", False):
            _LOGGER.warning("Désarmement en mode panique")

        return True
