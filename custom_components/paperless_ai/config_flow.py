import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

class PaperlessAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Beheer de configuratie flow voor Paperless-AI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Stap die wordt aangeroepen wanneer de gebruiker de integratie toevoegt."""
        errors = {}

        if user_input is not None:
            # Hier maken we de koppeling definitief
            return self.async_create_entry(
                title="Paperless-AI", 
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_API_KEY: user_input[CONF_API_KEY],
                }
            )

        # Het formulier met de exacte velden
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="http://192.168.50.39:3000"): str,
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )