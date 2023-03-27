from uuid import uuid4
from homeassistant.components.notify.const import (
    ATTR_TITLE,
    DOMAIN as NOTIFY_DOMAIN
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_ACTION, ATTR_DATA, ATTR_EVENT_MESSAGE
from custom_components.react.plugin.mobile_app.const import ATTR_ACTIONS, ATTR_PERSISTENT, ATTR_STICKY, ATTR_TAG, MESSAGE_CLEAR_NOTIFICATION
from custom_components.react.plugin.notify.const import FeedbackItem
from custom_components.react.plugin.notify.service import NotifyService


class MobileAppService(NotifyService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        data = {
            ATTR_EVENT_MESSAGE: message,
        }
        if feedback_items:
            data[ATTR_DATA] = {
                ATTR_ACTIONS:  [ {
                    ATTR_ACTION : item.feedback,
                    ATTR_TITLE : item.title
                } for item in feedback_items ],
                ATTR_PERSISTENT: "true",
                ATTR_TAG: uuid4().hex,
                ATTR_STICKY: "true"
            }

        await self.react.hass.services.async_call(
            NOTIFY_DOMAIN, 
            entity_id,
            data, 
            context
        )


    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        data = {
            ATTR_EVENT_MESSAGE: MESSAGE_CLEAR_NOTIFICATION,
            ATTR_DATA: {
                ATTR_TAG: conversation_id
            }
        }
        await self.react.hass.services.async_call(
            NOTIFY_DOMAIN, 
            message_id,
            data, 
            context
        )