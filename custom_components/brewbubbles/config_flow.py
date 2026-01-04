from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BrewBubblesClient, BrewBubblesCannotConnect, BrewBubblesInvalidResponse
from .const import DOMAIN, CONF_TEMPFORMAT, TEMP_C, TEMP_F


class BrewBubblesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required("host"): str}),
                errors=errors,
            )

        host = user_input["host"].strip()

        session = async_get_clientsession(self.hass)
        client = BrewBubblesClient(session, host)

        try:
            cfg = await client.get_config()
        except BrewBubblesCannotConnect:
            errors["base"] = "cannot_connect"
        except BrewBubblesInvalidResponse:
            errors["base"] = "invalid_response"
        except Exception:
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required("host"): str}),
                errors=errors,
            )

        # Pull identifiers from device config
        hostname = (cfg.get("hostname") or host).lower()
        bubble = cfg.get("bubble") or {}
        title_name = bubble.get("name") or hostname

        await self.async_set_unique_id(hostname)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Brew Bubbles - {title_name}",
            data={"host": host, "hostname": hostname},
        )
    
    @staticmethod
    def async_get_options_flow(config_entry):
        return BrewBubblesOptionsFlowHandler(config_entry)


class BrewBubblesOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is None:
            current = self._entry.options.get(CONF_TEMPFORMAT, TEMP_C)
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required(CONF_TEMPFORMAT, default=current): vol.In([TEMP_C, TEMP_F])
                }),
            )

        # push setting to device
        session = async_get_clientsession(self.hass)
        client = BrewBubblesClient(session, self._entry.data["host"])
        await client.set_temp_unit(user_input[CONF_TEMPFORMAT])

        return self.async_create_entry(title="", data=user_input)
