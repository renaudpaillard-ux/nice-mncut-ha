"""Config flow pour Nice MNCUT."""

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_IP, CONF_PIN


class NiceMncutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flux de configuration pour Nice MNCUT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gère la configuration utilisateur."""
        errors = {}

        if user_input is not None:
            # Validation basique
            if not user_input[CONF_IP]:
                errors[CONF_IP] = "invalid_ip"
            elif not user_input[CONF_PIN]:
                errors[CONF_PIN] = "invalid_pin"
            else:
                # Vérifier qu'il n'existe pas déjà une entrée pour cette IP
                await self.async_set_unique_id(user_input[CONF_IP])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Nice MNCUT ({user_input[CONF_IP]})",
                    data=user_input,
                )

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