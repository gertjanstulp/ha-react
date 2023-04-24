from telegram.utils.helpers import escape_markdown

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.telegram.notify import (
    ATTR_INLINE_KEYBOARD
)
from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID,
    ATTR_KEYBOARD_INLINE,
    ATTR_MESSAGE,
    ATTR_MESSAGEID,
    DOMAIN, 
    SERVICE_EDIT_MESSAGE,
)
from homeassistant.core import Context

from custom_components.react.const import (
    ATTR_DATA, 
    ATTR_EVENT_MESSAGE
)
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.provider import NotifyProvider
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()


class TelegramProvider(NotifyProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    def _debug(self, message: str):
        _LOGGER.debug(f"Telegram app plugin: TelegramProvider - {message}")


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        self._debug(f"Sending message to {entity_id}")
        data: dict = {
            ATTR_EVENT_MESSAGE: escape_markdown(message),
        }
        
        if feedback_items:
            data[ATTR_DATA] = {
                ATTR_INLINE_KEYBOARD : ", ".join(
                    map(lambda x: " ".join([ f"{x.title}:/react", x.feedback, x.acknowledgement ]), 
                    feedback_items)
                )
            }

        await self.hass_api.async_hass_call_service(
            NOTIFY_DOMAIN, 
            entity_id,
            data, 
            context
        )


    async def async_confirm_feedback(self, 
        context: Context, 
        conversation_id: str, 
        message_id: str, 
        text: str, 
        feedback: str,
        acknowledgement: str,
    ):
        self._debug(f"Confirming feedback '{feedback}' with acknowledgement '{acknowledgement}'")
        data = {
            ATTR_MESSAGEID: message_id,
            ATTR_CHAT_ID: conversation_id,
            ATTR_MESSAGE: escape_markdown(f"{text} - {acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
        await self.hass_api.async_hass_call_service(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            service_data=data, 
            context=context,
        )
