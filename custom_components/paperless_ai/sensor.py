import requests
import logging
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_HOST, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    host = config[CONF_HOST]
    api_key = config[CONF_API_KEY]

    async_add_entities([
        PaperlessTotalDocsSensor(host, api_key),
        PaperlessAiProcessedSensor(host, api_key),
        PaperlessUnprocessedSensor(host, api_key),
        PaperlessTotalTagsSensor(host, api_key),
        PaperlessTotalCorrespondentsSensor(host, api_key),
        PaperlessProcessedTodaySensor(host, api_key),
        PaperlessTokenUsageSensor(host, api_key),
        PaperlessSystemStatusSensor(host, api_key)
    ], True)

class PaperlessBaseSensor(SensorEntity):
    has_entity_name = True
    def __init__(self, host, api_key, name, unique_id, icon):
        self._host = host
        self._api_key = api_key
        self._attr_name = name
        self._attr_unique_id = f"{unique_id}_{host}"
        self._attr_icon = icon
        self._state = None

    @property
    def native_value(self):
        return self._state

class PaperlessTotalDocsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Documents", "paperless_total_docs", "mdi:file-document-multiple")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/manual/documents", headers={"x-api-key": self._api_key}, timeout=10)
            data = r.json()
            # Als de API een dict met 'data' teruggeeft ipv een list:
            self._state = len(data.get("data", data)) if isinstance(data, (list, dict)) else 0
        except Exception: self._state = None

class PaperlessAiProcessedSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "AI Processed", "paperless_ai_processed", "mdi:robot-check")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/manual/documents", headers={"x-api-key": self._api_key}, timeout=10)
            docs = r.json().get("data", r.json())
            self._state = len([d for d in docs if d.get('ai_processed') is True or d.get('ai_processed') == 1])
        except Exception: self._state = None

class PaperlessUnprocessedSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Unprocessed", "paperless_unprocessed", "mdi:file-clock")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/manual/documents", headers={"x-api-key": self._api_key}, timeout=10)
            docs = r.json().get("data", r.json())
            processed = len([d for d in docs if d.get('ai_processed') is True or d.get('ai_processed') == 1])
            self._state = len(docs) - processed
        except Exception: self._state = None

class PaperlessTotalTagsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Tags", "paperless_total_tags", "mdi:tag-multiple")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/manual/tags", headers={"x-api-key": self._api_key}, timeout=10)
            data = r.json()
            self._state = len(data.get("data", data))
        except Exception: self._state = None

class PaperlessTotalCorrespondentsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Correspondents", "paperless_total_corr", "mdi:account-arrow-right")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/manual/documents", headers={"x-api-key": self._api_key}, timeout=10)
            docs = r.json().get("data", r.json())
            corrs = {d.get('correspondent') for d in docs if d.get('correspondent')}
            self._state = len(corrs)
        except Exception: self._state = None

class PaperlessTokenUsageSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Tokens Used", "paperless_tokens", "mdi:counter")
        self._attr_native_unit_of_measurement = "tokens"
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/api/history", headers={"x-api-key": self._api_key}, timeout=10)
            self._state = r.json().get("total_tokens_used", 0)
        except Exception: self._state = 0

class PaperlessProcessedTodaySensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Processed Today", "paperless_processed_today", "mdi:calendar-check")
        self._attr_native_unit_of_measurement = "docs"
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/api/history", headers={"x-api-key": self._api_key}, timeout=10)
            today = datetime.now().strftime('%Y-%m-%d')
            history = r.json().get("data", [])
            count = len([h for h in history if h.get('created_at', '').startswith(today)])
            self._state = count
        except Exception: self._state = 0

class PaperlessSystemStatusSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "System Status", "paperless_system_status", "mdi:server-network")
    
    def update(self):
        try:
            r = requests.get(f"{self._host}/api/history", headers={"x-api-key": self._api_key}, timeout=10)
            if r.status_code == 200:
                self._state = "System Idle"
            else:
                self._state = "Error"
        except Exception: self._state = "Offline"