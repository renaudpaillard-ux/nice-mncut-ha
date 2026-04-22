"""Config flow pour Nice MNCUT."""

import asyncio
import ipaddress
import logging

import voluptuous as vol
import websockets
from homeassistant import config_entries

from .const import DOMAIN, CONF_IP, CONF_PIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(data: dict[str, str]) -> None:
    """Valide les données utilisateur et teste la connectivité au port WebSocket."""
    ipaddress.ip_address(data[CONF_IP])

    pin = data[CONF_PIN].strip()
    if not pin or not pin.isdigit():
        raise ValueError("invalid_pin")

    connection = None
    try:
        connection = await asyncio.wait_for(
            websockets.connect(
                f"ws://{data[CONF_IP]}:4012/",
                ping_interval=None,
                ping_timeout=None,
                close_timeout=2,
            ),
            timeout=5,
        )
    finally:
        if connection is not None:
            await connection.close()


class NiceMncutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flux de configuration pour Nice MNCUT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gère la configuration utilisateur."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                # Vérifier qu'il n'existe pas déjà une entrée pour cette IP
                await self.async_set_unique_id(user_input[CONF_IP])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Nice MNCUT ({user_input[CONF_IP]})",
                    data=user_input,
                )
            except ValueError as err:
                if str(err) == "invalid_pin":
                    errors[CONF_PIN] = "invalid_pin"
                else:
                    errors[CONF_IP] = "invalid_ip"
            except (OSError, TimeoutError, websockets.WebSocketException):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Nice MNCUT → Erreur inattendue dans config flow")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP): str,
                vol.Required(CONF_PIN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Permet de modifier l'adresse IP sans supprimer l'entrée."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input({
                    CONF_IP: user_input[CONF_IP],
                    CONF_PIN: self._get_reconfigure_entry().data[CONF_PIN],
                })
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates={CONF_IP: user_input[CONF_IP]},
                    title=f"Nice MNCUT ({user_input[CONF_IP]})",
                )
            except ValueError:
                errors[CONF_IP] = "invalid_ip"
            except (OSError, TimeoutError, websockets.WebSocketException):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Nice MNCUT → Erreur inattendue lors de la reconfiguration")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({vol.Required(CONF_IP): str}),
            errors=errors,
        )
