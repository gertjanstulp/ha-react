from telegram.helpers import escape_markdown

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.telegram.notify import ATTR_INLINE_KEYBOARD
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
from custom_components.react.plugin.telegram.config import TelegramConfig
from custom_components.react.utils.session import Session


class TelegramProvider(NotifyProvider[TelegramConfig]):

    async def async_notify(self, session: Session, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        session.debug(self.logger, f"Sending message to {entity_id}")
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

        await self.plugin.hass_api.async_hass_call_service(
            NOTIFY_DOMAIN, 
            entity_id,
            service_data=data, 
            context=context
        )


    async def async_confirm_feedback(self, 
        session: Session,
        context: Context, 
        conversation_id: str, 
        message_id: str, 
        text: str, 
        feedback: str,
        acknowledgement: str,
    ):
        session.debug(self.logger, f"Confirming feedback '{feedback}' with acknowledgement '{acknowledgement}'")
        data = {
            ATTR_MESSAGEID: message_id,
            ATTR_CHAT_ID: conversation_id,
            ATTR_MESSAGE: escape_markdown(f"{text} - {acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
        await self.plugin.hass_api.async_hass_call_service(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            service_data=data, 
            context=context,
        )
