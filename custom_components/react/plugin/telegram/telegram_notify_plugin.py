from __future__ import annotations

from typing import Union
from telegram.utils.helpers import escape_markdown
from homeassistant.const import ATTR_COMMAND, Platform
from homeassistant.core import Event, Context
from homeassistant.components.telegram_bot import (
    ATTR_ARGS,
    ATTR_CHAT_ID, 
    ATTR_KEYBOARD_INLINE, 
    ATTR_MESSAGE, 
    ATTR_MESSAGEID, 
    ATTR_TEXT,
    ATTR_USER_ID,
    DOMAIN, 
    EVENT_TELEGRAM_CALLBACK,
    SERVICE_EDIT_MESSAGE
)

from ..notify_plugin import NotifyPlugin, NotifyFeedbackEventDataReader, NotifySendMessageReactionEventDataReader
from ...base import ReactBase

from ...const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_TITLE,
    ATTR_EVENT_MESSAGE,
    ATTR_TYPE,
    EVENTDATA_COMMAND_REACT,
    REACT_ACTION_FEEDBACK,
    REACT_TYPE_NOTIFY
)

# Service data attributes
ATTR_SERVICE_DATA_INLINE_KEYBOARD = "inline_keyboard"


def setup_plugin(react: ReactBase):
    return TelegramNotifyPlugin(react)


class TelegramNotifyPlugin(NotifyPlugin):
    
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def feedback_event(self):
        return EVENT_TELEGRAM_CALLBACK

    
    def get_notify_send_message_reader_type(self) -> type[NotifySendMessageReactionEventDataReader]:
        return TelegramNotifySendMessageReactionEventDataReader


    def get_notify_feedback_reader_type(self) -> type[NotifyFeedbackEventDataReader]:
        return TelegramNotifyFeedbackEventDataReader


    async def async_send_notification(self, entity: str, data: dict, context: Context):
        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            entity,
            data, 
            context)


    async def async_acknowledge_feedback(self, feedback_data: dict, context: Context) -> None:
        await self.react.hass.services.async_call(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            feedback_data, 
            context=context)


class TelegramNotifySendMessageReactionEventDataReader(NotifySendMessageReactionEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


    def create_service_data(self) -> dict:
        result: dict = {
            ATTR_EVENT_MESSAGE: escape_markdown(self.message),
        }
        
        if self.feedback_items_raw:
            result[ATTR_DATA] = {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD : ", ".join(
                    map(lambda x: " ".join([
                        f"{x.get(ATTR_EVENT_FEEDBACK_ITEM_TITLE, None)}:/react", 
                        x.get(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, None), 
                        x.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT)
                    ]), 
                    self.feedback_items_raw)
                )
            }

        return result


class TelegramNotifyFeedbackEventDataReader(NotifyFeedbackEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
        
        self.event_type = event.event_type
        self.telegram_command = event.data.get(ATTR_COMMAND, None)
    
        self.user_id: Union[str, None] = None
        self.chat_id: Union[str, None] = None
        self.message_id: Union[str, None] = None
        self.message: Union[dict, None] = None
        

    def load(self):
        args: list = self.event.data.get(ATTR_ARGS, None)
        if args:
            self.feedback = args[0] if len(args) > 0 else None
            self.acknowledgement = args[1] if len(args) > 1 else None
        
        self.message = self.event.data.get(ATTR_MESSAGE, None)
        
        self.user_id = self.event.data.get(ATTR_USER_ID, None)
        self.chat_id = self.event.data.get(ATTR_CHAT_ID, None)
        if self.user_id:
            self.entity = self.react.configuration.workflow_config.entity_maps_config.get(self.user_id, None)
        if not self.entity and self.chat_id:
            self.entity = self.react.configuration.workflow_config.entity_maps_config.get(self.chat_id)
        if not self.entity:
            self.entity = "unknown"

        if self.message:
            self.message_id = self.message.get(ATTR_MESSAGEID, None)
            self.message_text = self.message.get(ATTR_TEXT, None)
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_TELEGRAM_CALLBACK and
            self.telegram_command == EVENTDATA_COMMAND_REACT
        )

    
    def create_action_event_data(self) -> dict:
        return {
            ATTR_ENTITY: self.entity,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.feedback
            }
        }


    def create_feedback_data(self) -> dict:
        return {
            ATTR_MESSAGEID: self.message_id,
            ATTR_CHAT_ID: self.chat_id,
            ATTR_MESSAGE: escape_markdown(f"{self.message_text} - {self.acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
