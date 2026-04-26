import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

class PaperlessAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Beheer de configuratie flow voor Paperless-AI."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Paperless-AI", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,  # Geen default meer
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )