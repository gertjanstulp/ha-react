from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.const import Platform
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_DATA, ATTR_EVENT_FEEDBACK_ITEMS, ATTR_EVENT_MESSAGE
from custom_components.react.plugin.common import NotifySendMessageReactionEventData, NotifySendMessageReactionEventFeedbackItem, NotifySendMessageReactionEventNotificationData
from custom_components.react.plugin.notify_plugin import NotifySendMessageReactionEvent
from custom_components.react.plugin.telegram.const import ATTR_SERVICE_DATA_INLINE_KEYBOARD, PLUGIN_NAME
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.struct import DynamicData


class TelegramNotifySendMessageTask(DefaultReactionTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, TelegramNotifySendMessageReactionEvent)


    async def async_execute_default(self, action_event: TelegramNotifySendMessageReactionEvent):
        self.react.log.debug("TelegramNotifyPlugin: sending notification to telegram")
        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            action_event.data.entity,
            action_event.data.data.create_service_data(), 
            action_event.context)


class TelegramNotifySendMessageReactionEventNotificationData(DynamicData):
    type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: NotifySendMessageReactionEventFeedbackItem }

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.feedback_items: list[NotifySendMessageReactionEventFeedbackItem] = None

        self.load(source)


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


    @property
    def applies(self) -> bool:
        return super().applies and self.data.data.plugin == PLUGIN_NAME
