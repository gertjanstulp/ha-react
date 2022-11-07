from homeassistant.const import Platform
from homeassistant.core import Context

from custom_components.react.base import ReactBase


SERVICE_CLOUD_SAY = "cloud_say"

class Api():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_speek(self, speek_data: dict, context: Context):
        await self.react.hass.services.async_call(
            Platform.TTS, 
            SERVICE_CLOUD_SAY,
            speek_data,
            context)