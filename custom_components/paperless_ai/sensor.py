import requests
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors via the config flow."""
    config = hass.data[DOMAIN][entry.entry_id]
    host = config[CONF_HOST]
    api_key = config[CONF_API_KEY]

    async_add_entities([
        PaperlessDocumentSensor(host, api_key),
        PaperlessHistorySensor(host, api_key)
    ], True)

class PaperlessDocumentSensor(SensorEntity):
    """Total Documents Sensor."""
    def __init__(self, host, api_key):
        self._host = host
        self._api_key = api_key
        self._state = None
        self._attr_name = "Paperless Total Documents"
        self._attr_unique_id = f"paperless_docs_{host}"
        self._attr_native_unit_of_measurement = "docs"
        self._attr_icon = "mdi:file-document-multiple"

    @property
    def native_value(self): return self._state

    def update(self):
        try:
            url = f"{self._host}/manual/documents"
            r = requests.get(url, headers={"x-api-key": self._api_key}, timeout=10)
            if r.status_code == 200:
                self._state = len(r.json())
        except Exception: self._state = None

class PaperlessHistorySensor(SensorEntity):
    """Last Activity Sensor."""
    def __init__(self, host, api_key):
        self._host = host
        self._api_key = api_key
        self._state = None
        self._attr = {}
        self._attr_name = "Paperless Last Activity"
        self._attr_unique_id = f"paperless_history_{host}"
        self._attr_icon = "mdi:history"

    @property
    def native_value(self): return self._state

    @property
    def extra_state_attributes(self): return self._attr

    def update(self):
        try:
            url = f"{self._host}/api/history"
            r = requests.get(url, headers={"x-api-key": self._api_key}, timeout=10)
            data = r.json().get("data", [])
            if data:
                last = data[0]
                self._state = last.get("title")
                self._attr = {
                    "correspondent": last.get("correspondent"),
                    "created_at": last.get("created_at")
                }
        except Exception: self._state = "Error"