from telegram.utils.helpers import escape_markdown

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
from homeassistant.const import Platform
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_DATA, ATTR_EVENT_MESSAGE
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.service import NotifyService


class TelegramService(NotifyService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
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

        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            entity_id,
            data, 
            context
        )


    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        data = {
            ATTR_MESSAGEID: message_id,
            ATTR_CHAT_ID: conversation_id,
            ATTR_MESSAGE: escape_markdown(f"{text} - {acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
        await self.react.hass.services.async_call(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            service_data=data, 
            context=context,
        )
