import requests
import logging
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    host = config[CONF_HOST]
    api_key = config[CONF_API_KEY]

    async_add_entities([
        PaperlessStatsSensor(host, api_key),
        PaperlessTokenSensor(host, api_key),
        PaperlessTaskSensor(host, api_key),
        PaperlessDocCountSensor(host, api_key)
    ], True)

class PaperlessDocCountSensor(SensorEntity):
    """Gedetailleerde document status (Total, AI Processed, Unprocessed)."""
    def __init__(self, host, api_key):
        self._host, self._api_key = host, api_key
        self._attr_name = "Paperless Document Status"
        self._attr_unique_id = f"paperless_docs_{host}"
        self._attr_icon = "mdi:file-document-multiple"
        self._state = None
        self._extra_attr = {}

    @property
    def native_value(self): return self._state
    @property
    def extra_state_attributes(self): return self._extra_attr

    def update(self):
        try:
            # We halen de lijst op om de echte counts te berekenen
            r = requests.get(f"{self._host}/manual/documents", headers={"x-api-key": self._api_key}, timeout=10)
            docs = r.json()
            total = len(docs)
            processed = len([d for d in docs if d.get('ai_processed') is True])
            self._state = total
            self._extra_attr = {
                "ai_processed": processed,
                "unprocessed": total - processed,
                "total_documents": total
            }
        except Exception as e: _LOGGER.error("Error updating doc sensor: %s", e)

class PaperlessStatsSensor(SensorEntity):
    """Systeem statistieken (Tags, Correspondents)."""
    def __init__(self, host, api_key):
        self._host, self._api_key = host, api_key
        self._attr_name = "Paperless System Statistics"
        self._attr_unique_id = f"paperless_stats_{host}"
        self._attr_icon = "mdi:chart-bar"
        self._state = None
        self._extra_attr = {}

    @property
    def native_value(self): return self._state
    @property
    def extra_state_attributes(self): return self._extra_attr

    def update(self):
        try:
            # Tags tellen
            t = requests.get(f"{self._host}/manual/tags", headers={"x-api-key": self._api_key}, timeout=10)
            tags_count = len(t.json())
            self._state = tags_count
            self._extra_attr = {"total_tags": tags_count}
        except Exception as e: _LOGGER.error("Error updating stats sensor: %s", e)

class PaperlessTokenSensor(SensorEntity):
    """AI Token Usage."""
    def __init__(self, host, api_key):
        self._host, self._api_key = host, api_key
        self._attr_name = "Paperless AI Tokens"
        self._attr_unique_id = f"paperless_tokens_{host}"
        self._attr_icon = "mdi:cpu-64-bit"
        self._state = 0
        self._extra_attr = {}

    @property
    def native_value(self): return self._state
    @property
    def extra_state_attributes(self): return self._extra_attr

    def update(self):
        try:
            r = requests.get(f"{self._host}/api/history", headers={"x-api-key": self._api_key}, timeout=10)
            data = r.json()
            # Hier tellen we de tokens op uit de historie (indien beschikbaar in API)
            self._state = data.get("total_tokens_used", 0)
            self._extra_attr = {
                "prompt_tokens": data.get("total_prompt_tokens", 0),
                "completion_tokens": data.get("total_completion_tokens", 0)
            }
        except Exception: pass

class PaperlessTaskSensor(SensorEntity):
    """Task Runner Status."""
    def __init__(self, host, api_key):
        self._host, self._api_key = host, api_key
        self._attr_name = "Paperless Task Status"
        self._attr_unique_id = f"paperless_task_{host}"
        self._attr_icon = "mdi:run-fast"
        self._state = "Idle"

    @property
    def native_value(self): return self._state

    def update(self):
        try:
            # We checken de system status
            r = requests.get(f"{self._host}/api/history", headers={"x-api-key": self._api_key}, timeout=10)
            if r.status_code == 200:
                self._state = "System Idle" # In een toekomstige API update kunnen we hier 'Processing' van maken
        except Exception: self._state = "Offline"