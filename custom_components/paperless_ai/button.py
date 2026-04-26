import requests
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up buttons via the config flow."""
    config = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PaperlessScanButton(config[CONF_HOST], config[CONF_API_KEY])])

class PaperlessScanButton(ButtonEntity):
    """Scan Now Button."""
    def __init__(self, host, api_key):
        self._host = host
        self._api_key = api_key
        self._attr_name = "Paperless Scan Now"
        self._attr_unique_id = f"paperless_scan_btn_{host}"
        self._attr_icon = "mdi:magnify-scan"

    def press(self):
        """Trigger the scan."""
        try:
            url = f"{self._host}/api/scan/now"
            requests.post(url, headers={"x-api-key": self._api_key}, timeout=10)
        except Exception: pass