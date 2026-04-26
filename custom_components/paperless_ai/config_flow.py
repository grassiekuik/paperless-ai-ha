import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

class PaperlessAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paperless-AI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user enters data."""
        errors = {}

        if user_input is not None:
            # You could add validation here (e.g., trying to connect to the host)
            return self.async_create_entry(title="Paperless-AI", data=user_input)

        # This defines the fields in the popup
        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="http://192.168.50.39:3000"): str,
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )