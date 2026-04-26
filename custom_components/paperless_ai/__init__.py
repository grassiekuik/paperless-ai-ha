from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paperless-AI from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # Store the config data so sensors/buttons can access it
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Tell HA to load sensor.py and button.py
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "button"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor", "button"])