import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

class PaperlessAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paperless-AI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Maak de integratie aan met de ingevoerde data
            return self.async_create_entry(title="Paperless-AI", data=user_input)

        # Het formulier dat de gebruiker ziet
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="http://192.168.50.39:3000"): str,
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )