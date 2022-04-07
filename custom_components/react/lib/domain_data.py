from dataclasses import field
from typing import Callable
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .. import const as co


class DomainData:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass


    async def init_config(self, config_entry: ConfigEntry):
        self.device_id = config_entry.unique_id


def get(hass: HomeAssistant) -> DomainData:
    if co.DOMAIN_DATA in hass.data:
        return hass.data[co.DOMAIN_DATA]
    ret = hass.data[co.DOMAIN_DATA] = DomainData(hass)
    return ret
