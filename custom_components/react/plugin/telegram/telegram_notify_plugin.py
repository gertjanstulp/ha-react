from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.const import Platform
from homeassistant.core import Event, Context
from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID, 
    ATTR_KEYBOARD_INLINE, 
    ATTR_MESSAGE, 
    ATTR_MESSAGEID, 
    DOMAIN, 
    EVENT_TELEGRAM_CALLBACK,
    SERVICE_EDIT_MESSAGE
)

from custom_components.react.base import ReactBase
from custom_components.react.utils.struct import DynamicData
from custom_components.react.plugin.notify_plugin import (
    NotifyFeedbackEvent,
    NotifyFeedbackEventData, 
    NotifyPlugin, 
    NotifySendMessageReactionEvent, 
    NotifySendMessageReactionEventData, 
    NotifySendMessageReactionEventNotificationData
)
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, 
    ATTR_EVENT_MESSAGE, 
    ATTR_TYPE, 
    EVENTDATA_COMMAND_REACT, 
    REACT_ACTION_FEEDBACK, 
    REACT_TYPE_NOTIFY
)


ATTR_SERVICE_DATA_INLINE_KEYBOARD = "inline_keyboard"


def setup_plugin(react: ReactBase):
    return TelegramNotifyPlugin(react)


class TelegramNotifyPlugin(NotifyPlugin):
    
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def feedback_event(self):
        return EVENT_TELEGRAM_CALLBACK

    
    def get_notify_send_message_event_type(self) -> type[NotifySendMessageReactionEvent]:
        return TelegramNotifySendMessageReactionEvent


    def get_notify_feedback_event_type(self) -> type[NotifyFeedbackEvent]:
        return TelegramNotifyFeedbackEvent


    async def async_send_notification(self, entity: str, notification_data: dict, context: Context):
        self.react.log.debug("TelegramNotifyPlugin: sending notification to telegram")
        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            entity,
            notification_data, 
            context)


    async def async_acknowledge_feedback(self, feedback_data: dict, context: Context) -> None:
        self.react.log.debug("TelegramNotifyPlugin: acknowledging feedback to telegram")
        await self.react.hass.services.async_call(
            DOMAIN,
            SERVICE_EDIT_MESSAGE,
            feedback_data, 
            context=context)


class TelegramNotifySendMessageReactionEventNotificationData(NotifySendMessageReactionEventNotificationData):
    def __init__(self, source: dict) -> None:
        super().__init__(source)


    def create_service_data(self) -> dict:
        result: dict = {
            ATTR_EVENT_MESSAGE: escape_markdown(self.message),
        }
        
        if self.feedback_items:
            result[ATTR_DATA] = {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD : ", ".join(
                    map(lambda x: " ".join([ f"{x.title}:/react", x.feedback, x.acknowledgement ]), 
                    self.feedback_items)
                )
            }

        return result


class TelegramNotifySendMessageReactionEventData(NotifySendMessageReactionEventData[TelegramNotifySendMessageReactionEventNotificationData]):
    def __init__(self) -> None:
        super().__init__(TelegramNotifySendMessageReactionEventNotificationData)


class TelegramNotifySendMessageReactionEvent(NotifySendMessageReactionEvent[TelegramNotifySendMessageReactionEventData]):

    def __init__(self, event: Event) -> None:
        super().__init__(event, TelegramNotifySendMessageReactionEventData)


class TelegramNotifyFeedbackEventDataMessage(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.message_id: str = None
        self.text: str = None

        self.load(source)


class TelegramNotifyFeedbackEventData(NotifyFeedbackEventData):
    type_hints: dict = { ATTR_MESSAGE: TelegramNotifyFeedbackEventDataMessage }

    def __init__(self) -> None:
        super().__init__()

        self.args: list = None
        self.command: str = None
        self.user_id: str = None
        self.chat_id: str = None
        self.message: TelegramNotifyFeedbackEventDataMessage = None


    def load(self, source: dict) -> None:
        super().load(source)
        if self.args:
            self.feedback = self.args[0] if len(self.args) > 0 else None
            self.acknowledgement = self.args[1] if len(self.args) > 1 else None


class TelegramNotifyFeedbackEvent(NotifyFeedbackEvent[TelegramNotifyFeedbackEventData]):

    def __init__(self, event: Event) -> None:
        super().__init__(event, TelegramNotifyFeedbackEventData)
        
        self.event_type = event.event_type
        if self.data.user_id:
            self.data.entity = self.data.user_id
        if not self.data.entity and self.data.chat_id:
            self.data.entity = self.data.chat_id
        if not self.data.entity:
            self.data.entity = "unknown"
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_TELEGRAM_CALLBACK and
            self.data.command == EVENTDATA_COMMAND_REACT
        )

    
    def create_action_event_data(self, react: ReactBase) -> dict:
        entity_maps = react.configuration.workflow_config.entity_maps_config
        return {
            ATTR_ENTITY: entity_maps.get(self.data.entity, None),
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.data.feedback
            }
        }


    def create_feedback_data(self, react: ReactBase) -> dict:
        return {
            ATTR_MESSAGEID: self.data.message.message_id,
            ATTR_CHAT_ID: self.data.chat_id,
            ATTR_MESSAGE: escape_markdown(f"{self.data.message.text} - {self.data.acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
