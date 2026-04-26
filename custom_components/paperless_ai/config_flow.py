import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "paperless_ai"

class PaperlessAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paperless-AI."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Paperless-AI", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="http://192.168.50.39:3000"): str,
                vol.Required("api_key"): str,
            })
        )