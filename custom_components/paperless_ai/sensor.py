import logging
import requests
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import StateType
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
    _attr_should_poll = True

    def __init__(self, host, api_key, name, unique_id, icon):
        self._host = host
        self._api_key = api_key
        self._attr_name = name
        self._attr_unique_id = f"{unique_id}_{host.replace('http://', '').replace(':', '_')}"
        self._attr_icon = icon
        self._state = None

    @property
    def native_value(self) -> StateType:
        return self._state

    def _get_data(self, endpoint):
        """Helper om data op te halen via een synchroon request."""
        try:
            url = f"{self._host}{endpoint}"
            headers = {"x-api-key": self._api_key}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _LOGGER.debug("Error fetching from %s: %s", endpoint, e)
            return None

class PaperlessTotalDocsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Documents", "paperless_total_docs", "mdi:file-document-multiple")
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/manual/documents")
        if data is not None:
            docs = data.get("data", data) if isinstance(data, dict) else data
            self._state = len(docs) if isinstance(docs, list) else 0

class PaperlessAiProcessedSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "AI Processed", "paperless_ai_processed", "mdi:robot-check")
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/manual/documents")
        if data is not None:
            docs = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(docs, list):
                self._state = len([d for d in docs if str(d.get('ai_processed')).lower() in ['true', '1']])

class PaperlessUnprocessedSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Unprocessed", "paperless_unprocessed", "mdi:file-clock")
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/manual/documents")
        if data is not None:
            docs = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(docs, list):
                processed = len([d for d in docs if str(d.get('ai_processed')).lower() in ['true', '1']])
                self._state = len(docs) - processed

class PaperlessTotalTagsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Tags", "paperless_total_tags", "mdi:tag-multiple")
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/manual/tags")
        if data is not None:
            tags = data.get("data", data) if isinstance(data, dict) else data
            self._state = len(tags) if isinstance(tags, list) else 0

class PaperlessTotalCorrespondentsSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Correspondents", "paperless_total_corr", "mdi:account-arrow-right")
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/manual/documents")
        if data is not None:
            docs = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(docs, list):
                self._state = len({d.get('correspondent') for d in docs if d.get('correspondent')})

class PaperlessTokenUsageSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Total Tokens Used", "paperless_tokens", "mdi:counter")
        self._attr_native_unit_of_measurement = "tokens"
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/api/history")
        if data:
            self._state = data.get("total_tokens_used", 0)

class PaperlessProcessedTodaySensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "Processed Today", "paperless_processed_today", "mdi:calendar-check")
        self._attr_native_unit_of_measurement = "docs"
    
    async def async_update(self):
        data = await self.hass.async_add_executor_job(self._get_data, "/api/history")
        if data:
            today = datetime.now().strftime('%Y-%m-%d')
            history = data.get("data", [])
            self._state = len([h for h in history if str(h.get('created_at', '')).startswith(today)])

class PaperlessSystemStatusSensor(PaperlessBaseSensor):
    def __init__(self, host, api_key):
        super().__init__(host, api_key, "System Status", "paperless_system_status", "mdi:server-network")
    
    async def async_update(self):
        try:
            url = f"{self._host}/api/history"
            headers = {"x-api-key": self._api_key}
            response = await self.hass.async_add_executor_job(
                lambda: requests.get(url, headers=headers, timeout=10)
            )
            self._state = "System Idle" if response.status_code == 200 else "Error"
        except Exception:
            self._state = "Offline"