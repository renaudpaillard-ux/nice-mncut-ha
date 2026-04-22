"""
Nice MNCUT V1 Integration - Home Assistant
Architecture avec Hub WebSocket centralisé et Coordinator

Version: 1.0.0
Date: 2026-04-21
Changelog:
- v1.0.0: Version initiale stable avec binary sensors et alarm panel
"""

import asyncio
import logging
import re
import time
from collections.abc import Callable
from contextlib import suppress

import websockets
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import Platform

from .const import DOMAIN, CONF_IP, CONF_PIN, STX, ETX, WS_TARGET_ID, WS_PAIRING_USERNAME, WS_PAIRING_PASSWORD

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.ALARM_CONTROL_PANEL, Platform.BINARY_SENSOR, Platform.SENSOR]
SERVICE_CLEAR_ANOMALIES = "clear_anomalies"


class NiceMncutHub:
    """Hub centralisé pour gérer la connexion WebSocket Nice MNCUT."""

    def __init__(self, ip: str, pin: str):
        self.ip = ip
        self.pin = pin
        self._ws = None
        self._listeners: list[Callable[[], None]] = []
        self._running = False
        self._reconnect_task: asyncio.Task | None = None
        self._last_message_time: float | None = None

        # État partagé
        self.state = {
            "raw_state": None,
            "areas": {},
            "armed_status": "unavailable",
            "battery_low": False,
            "battery_level": None,  # Niveau batterie en %
            "power_ok": True,
            "sabotage": False,
            "contact_open": False,
            "sensor_triggered": False,
            "panic": False,
            "maintenance": False,
            "exit_delay": None,
            "exit_delay_start": None,
        }

    @property
    def available(self) -> bool:
        """Retourne True si le hub est connecté."""
        return self._ws is not None

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Ajoute un callback pour être notifié des changements d'état."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Retire un callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    async def _notify_listeners(self):
        """Notifie tous les listeners."""
        for callback in self._listeners:
            try:
                callback()
            except Exception as e:
                _LOGGER.error("Erreur lors de la notification : %s", e)

    async def start(self):
        """Démarre la connexion WebSocket."""
        self._running = True
        self._reconnect_task = asyncio.create_task(self._maintain_connection())

    async def stop(self):
        """Arrête la connexion WebSocket."""
        self._running = False
        if self._reconnect_task:
            self._reconnect_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reconnect_task
            self._reconnect_task = None
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def _maintain_connection(self):
        """Maintient la connexion WebSocket active."""
        uri = f"ws://{self.ip}:4012/"

        while self._running:
            try:
                async with websockets.connect(
                    uri, 
                    ping_interval=None, 
                    ping_timeout=None, 
                    max_size=None,
                    close_timeout=5
                ) as ws:
                    self._ws = ws
                    self._last_message_time = time.time()
                    _LOGGER.info("Nice MNCUT → Connecté au WebSocket")

                    # LOGIN
                    source = str(int(time.time() * 1000))
                    login = (
                        f'<?xml version="1.0"?>'
                        f'<Request id="main_obj" source="{source}" target="{WS_TARGET_ID}" '
                        f'type="PAIRING"><Authentication username="{WS_PAIRING_USERNAME}" password="{WS_PAIRING_PASSWORD}"/></Request>'
                    )
                    await ws.send(STX + login.encode() + ETX)
                    _LOGGER.debug("Nice MNCUT → LOGIN envoyé")

                    # Demande de l'état complet (type STATUS)
                    await asyncio.sleep(0.5)
                    status_request = (
                        f'<?xml version="1.0" encoding="utf-8"?>'
                        f'<Request id="00" source="{source}" target="{WS_TARGET_ID}" '
                        f'protocolVersion="1.0" type="STATUS"/>'
                    )
                    await ws.send(STX + status_request.encode() + ETX)
                    _LOGGER.debug("Nice MNCUT → STATUS request envoyé")

                    # Tâche de surveillance (heartbeat)
                    heartbeat_task = asyncio.create_task(self._heartbeat())

                    try:
                        # Écoute des messages avec timeout
                        async for msg in ws:
                            self._last_message_time = time.time()
                            await self._process_message(msg)
                    finally:
                        heartbeat_task.cancel()

            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.warning(
                    "Nice MNCUT → Erreur WebSocket (%s). Reconnexion dans 5s...", e
                )
                self._ws = None
                # Marquer les entités comme indisponibles
                self.state["armed_status"] = "unavailable"
                await self._notify_listeners()
                await asyncio.sleep(5)

    async def _heartbeat(self):
        """Vérifie que des messages arrivent régulièrement."""
        while True:
            await asyncio.sleep(60)  # Vérification toutes les 60 secondes
            if self._last_message_time:
                elapsed = time.time() - self._last_message_time
                if elapsed > 120:  # Pas de message depuis 2 minutes
                    _LOGGER.warning(
                        "Nice MNCUT → Aucun message depuis %d secondes, reconnexion...", 
                        int(elapsed)
                    )
                    if self._ws:
                        await self._ws.close()
                    break

    async def _process_message(self, msg: bytes):
        """Traite un message WebSocket."""
        if b"<State>" not in msg:
            return

        # Traiter AL010 pour le niveau de batterie
        if b"<Device>AL010</Device>" in msg and b"<Info>" in msg:
            try:
                info = msg.split(b"<Info>")[1].split(b"</Info>")[0].decode()
                # Extraire le pourcentage (ex: "53%")
                battery_percent = int(info.replace("%", ""))
                self.state["battery_level"] = battery_percent
                _LOGGER.debug("Nice MNCUT → Niveau batterie: %s%%", battery_percent)
                await self._notify_listeners()
            except (IndexError, UnicodeDecodeError, ValueError) as err:
                _LOGGER.debug("Nice MNCUT → Impossible de parser le niveau batterie: %s", err)
            return

        # Traiter AL002 pour l'état de la centrale
        if b"<Device>AL002</Device>" not in msg:
            return

        # Extraction du raw_state
        try:
            raw_state = msg.split(b"<State>")[1].split(b"</State>")[0].decode()
            self.state["raw_state"] = raw_state
        except (IndexError, UnicodeDecodeError):
            raw_state = None

        # Extraction des zones et délai de sortie
        area_re = re.compile(rb'<Area id="(\d+)" st="(\d+)"(?:\s+texit="(\d+)")?')
        areas = {}
        exit_delay = None
        
        for match in area_re.findall(msg):
            zid = int(match[0])
            st = int(match[1])
            areas[zid] = st
            # Si texit est présent et qu'on est en armement (st=1)
            if match[2] and st == 1:
                exit_delay = int(match[2])
        
        self.state["areas"] = areas

        # Détection anomalies
        has_anoms = b"<Anoms" in msg and b"warning=" in msg
        
        # Contact ouvert : présence de S00903 dans les anomalies
        has_anom_entries = b"<Anom id=" in msg
        contact_open_anom = has_anoms and has_anom_entries and b"S00903" in msg
        
        # Capteur déclenché : S00902 dans les anomalies
        sensor_triggered_anom = has_anoms and has_anom_entries and b"S00902" in msg
        
        # Sabotage boîtier : S00144 dans les anomalies
        sabotage_anom = has_anoms and has_anom_entries and b"S00144" in msg
        
        # Coupure secteur : S10136 dans les anomalies ou S10102 dans raw_state
        power_failure_anom = has_anoms and has_anom_entries and b"S10136" in msg

        # Analyse de l'état
        rs = raw_state or ""

        # États binaires
        self.state["battery_low"] = rs.startswith("S10401")
        self.state["power_ok"] = not (rs.startswith("S10102") or power_failure_anom)
        self.state["panic"] = rs.startswith("S2")
        self.state["maintenance"] = rs in ("S00124", "S00125")

        # Sabotage ou agression
        # S3xxx = Agression, S4xxx = Sabotage capteur, S00144 = Sabotage centrale (boîtier ouvert)
        # S00144 peut être soit dans raw_state soit dans les anomalies
        self.state["sabotage"] = rs.startswith("S3") or rs.startswith("S4") or rs == "S00144" or sabotage_anom

        # Contact ouvert et capteur déclenché via anomalies
        self.state["contact_open"] = contact_open_anom
        self.state["sensor_triggered"] = sensor_triggered_anom

        _LOGGER.debug(
            "Nice MNCUT → Anomalies détectées: contact_ouvert=%s, capteur_déclenché=%s, sabotage=%s, coupure_secteur=%s",
            contact_open_anom, sensor_triggered_anom, sabotage_anom, power_failure_anom
        )

        # État d'armement (plus d'état triggered)
        if rs == "S00126":
            # S00126 = transition (arming ou disarming)
            prev_status = self.state.get("armed_status", "disarmed")
            if prev_status == "disarmed":
                armed_status = "arming"
            else:
                armed_status = "disarming"
        elif rs == "S00121" and all(v == 0 for v in areas.values()):
            armed_status = "disarmed"
            # Réinitialiser le délai de sortie
            self.state["exit_delay"] = None
            self.state["exit_delay_start"] = None
        elif rs == "S00120":
            # S00120 = armement total
            if any(v == 1 for v in areas.values()):
                armed_status = "arming"
                # Démarrer le décompte si on a un texit
                if exit_delay and not self.state["exit_delay_start"]:
                    self.state["exit_delay"] = exit_delay
                    self.state["exit_delay_start"] = time.time()
                    _LOGGER.debug("Nice MNCUT → Décompte de sortie démarré: %ds", exit_delay)
            elif all(v == 2 for v in areas.values()):
                armed_status = "armed_away"
                # Fin du décompte
                self.state["exit_delay"] = None
                self.state["exit_delay_start"] = None
            else:
                armed_status = "armed_away"
        elif rs == "S00122":
            # S00122 = armement partiel
            if any(v == 1 for v in areas.values()):
                armed_status = "arming"
                # Démarrer le décompte si on a un texit
                if exit_delay and not self.state["exit_delay_start"]:
                    self.state["exit_delay"] = exit_delay
                    self.state["exit_delay_start"] = time.time()
                    _LOGGER.debug("Nice MNCUT → Décompte de sortie démarré: %ds", exit_delay)
            else:
                armed_status = "armed_home"
                # Fin du décompte
                self.state["exit_delay"] = None
                self.state["exit_delay_start"] = None
        elif areas:
            # Fallback sur les zones
            if all(v == 0 for v in areas.values()):
                armed_status = "disarmed"
            elif all(v == 2 for v in areas.values()):
                armed_status = "armed_away"
            elif any(v == 2 for v in areas.values()):
                armed_status = "armed_home"
            else:
                armed_status = "unavailable"
        else:
            armed_status = "unavailable"

        self.state["armed_status"] = armed_status

        _LOGGER.debug(
            "Nice MNCUT → État mis à jour: %s (raw: %s, zones: %s, contact_ouvert: %s)", 
            armed_status, rs, areas, self.state["contact_open"]
        )

        # Notifier les listeners (TOUJOURS, même si armed_status n'a pas changé)
        await self._notify_listeners()

    async def send_command(self, cmd: str, areas: str = "123456"):
        """Envoie une commande à la centrale."""
        if not self._ws:
            _LOGGER.error("Nice MNCUT → WebSocket non connecté")
            return False

        source = str(int(time.time() * 1000))
        cmd_xml = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<Request id="00" source="{source}" target="{WS_TARGET_ID}" '
            f'protocolVersion="1.0" type="DEVICE_CMD">'
            f'<Command>{cmd}</Command>'
            f'<Device>AL002</Device>'
            f'<Arguments>'
            f'<Argument id="PIN">{self.pin}</Argument>'
            f'<Argument id="AREAS">{areas}</Argument>'
            f'</Arguments>'
            f'</Request>'
        )

        try:
            await self._ws.send(STX + cmd_xml.encode() + ETX)
            _LOGGER.info("Nice MNCUT → Commande envoyée: %s (%s)", cmd, areas)
            _LOGGER.debug("Nice MNCUT → CMD XML: %s", cmd_xml[:100])
            return True

        except Exception as e:
            _LOGGER.error("Nice MNCUT → Erreur envoi commande: %s", e)
            return False

    async def clear_anomalies(self, areas: str = "123456"):
        """Acquitte les anomalies avec séquence complète LOGIN → ANOM_ACK."""
        _LOGGER.debug("Nice MNCUT → clear_anomalies appelé")
        
        if not self._ws:
            _LOGGER.error("Nice MNCUT → WebSocket non connecté")
            return False

        source = str(int(time.time() * 1000))
        
        # 1. LOGIN normal (TERM_CODE)
        login_normal = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<Request id="widget_login" source="{source}" target="{WS_TARGET_ID}" '
            f'protocolVersion="1.0" type="MENU">'
            f'<filter>USER|POWERUSER</filter>'
            f'<act>LOGIN</act>'
            f'<page>USER</page>'
            f'<par><code>{self.pin}</code><type>TERM_CODE</type></par>'
            f'</Request>'
        )
        
        # 2. LOGIN forcé (TERM_CODE_FORCE)
        login_force = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<Request id="widget_sideanom" source="{source}" target="{WS_TARGET_ID}" '
            f'protocolVersion="1.0" type="MENU">'
            f'<filter>USER|POWERUSER</filter>'
            f'<act>LOGIN</act>'
            f'<page>USER</page>'
            f'<par><code>{self.pin}</code><type>TERM_CODE_FORCE</type></par>'
            f'</Request>'
        )
        
        # 3. ANOM_ACK
        ack_xml = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<Request id="00" source="{source}" target="{WS_TARGET_ID}" '
            f'protocolVersion="1.0" type="STATE">'
            f'<type>ANOM_ACK</type>'
            f'<value>{areas}</value>'
            f'</Request>'
        )
        
        # 4. Commande vide (validation)
        cmd_empty = (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<Request id="00" source="{source}" target="{WS_TARGET_ID}" '
            f'protocolVersion="1.0" type="DEVICE_CMD">'
            f'<Command></Command>'
            f'<Device>AL002</Device>'
            f'<Arguments>'
            f'<Argument id="PIN">{self.pin}</Argument>'
            f'<Argument id="AREAS">------</Argument>'
            f'</Arguments>'
            f'</Request>'
        )

        try:
            # Séquence complète
            await self._ws.send(STX + login_normal.encode() + ETX)
            _LOGGER.debug("Nice MNCUT → LOGIN normal envoyé")
            await asyncio.sleep(0.3)
            
            await self._ws.send(STX + login_force.encode() + ETX)
            _LOGGER.debug("Nice MNCUT → LOGIN FORCE envoyé")
            await asyncio.sleep(0.3)
            
            await self._ws.send(STX + ack_xml.encode() + ETX)
            _LOGGER.info("Nice MNCUT → ANOM_ACK envoyé")
            await asyncio.sleep(0.3)
            
            await self._ws.send(STX + cmd_empty.encode() + ETX)
            _LOGGER.debug("Nice MNCUT → Commande vide (validation) envoyée")
            
            return True

        except Exception as e:
            _LOGGER.error("Nice MNCUT → Erreur acquittement anomalies: %s", e, exc_info=True)
            return False


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Pas de support YAML."""
    return True


async def async_handle_clear_anomalies(call: ServiceCall) -> None:
    """Acquitte les anomalies sur tous les hubs connectés."""
    hubs: dict[str, NiceMncutHub] = call.hass.data.get(DOMAIN, {})
    areas = call.data.get("areas", "123456")

    tasks = [hub.clear_anomalies(areas) for hub in hubs.values() if hub.available]
    if not tasks:
        _LOGGER.warning("Nice MNCUT → Aucun hub connecté pour le service clear_anomalies")
        return

    await asyncio.gather(*tasks)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration de l'intégration via config_entry."""
    hass.data.setdefault(DOMAIN, {})

    ip = entry.data[CONF_IP]
    pin = entry.data[CONF_PIN]

    # Création du Hub
    hub = NiceMncutHub(ip, pin)
    hass.data[DOMAIN][entry.entry_id] = hub

    # Démarrage du Hub
    await hub.start()

    if not hass.services.has_service(DOMAIN, SERVICE_CLEAR_ANOMALIES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_ANOMALIES,
            async_handle_clear_anomalies,
        )
        _LOGGER.info("Nice MNCUT : service clear_anomalies enregistré")

    # Chargement des plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Déchargement de l'entrée."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hub = hass.data[DOMAIN].pop(entry.entry_id)
        await hub.stop()
        if not hass.data[DOMAIN] and hass.services.has_service(DOMAIN, SERVICE_CLEAR_ANOMALIES):
            hass.services.async_remove(DOMAIN, SERVICE_CLEAR_ANOMALIES)

    return unload_ok
