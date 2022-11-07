from homeassistant.const import Platform
from homeassistant.core import Context
from homeassistant.components.telegram_bot import (
    DOMAIN, 
    SERVICE_EDIT_MESSAGE
)

from custom_components.react.base import ReactBase


class Api():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_send_message(self, entity: str, message_data: dict, context: Context):
        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            entity,
            message_data, 
            context)


    async def async_confirm_feedback(self, feedback_data: dict, context: Context):
        await self.react.hass.services.async_call(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            service_data=feedback_data, 
            context=context)