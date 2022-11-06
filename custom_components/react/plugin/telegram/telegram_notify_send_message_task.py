from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_DATA, ATTR_EVENT_FEEDBACK_ITEMS, ATTR_EVENT_MESSAGE, REACT_ACTION_SEND_MESSAGE, REACT_TYPE_NOTIFY
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.telegram.telegram_plugin import ATTR_SERVICE_DATA_INLINE_KEYBOARD, PLUGIN_NAME
from custom_components.react.plugin.telegram.telegram_api import TelegramApi


class TelegramNotifySendMessageTask(DefaultReactionTask):
    def __init__(self, react: ReactBase, telegram_api: TelegramApi) -> None:
        super().__init__(react, TelegramNotifySendMessageReactionEvent)
        self.telegram_api = telegram_api


    async def async_execute_default(self, action_event: TelegramNotifySendMessageReactionEvent):
        self.react.log.debug("TelegramNotifyPlugin: sending notification to telegram")
        await self.telegram_api.async_send_message(
            action_event.payload.entity,
            action_event.create_message_data(),
            action_event.context
        )


class TelegramNotifySendMessageReactionEventFeedbackItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.title: str = None
        self.feedback: str = None
        self.acknowledgement: str = None

        self.load(source)


class TelegramNotifySendMessageReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: TelegramNotifySendMessageReactionEventFeedbackItem }

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.feedback_items: list[TelegramNotifySendMessageReactionEventFeedbackItem] = None

        self.load(source)


class TelegramNotifySendMessageReactionEvent(ReactionEvent[TelegramNotifySendMessageReactionEventData]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, TelegramNotifySendMessageReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_SEND_MESSAGE and 
            self.payload.data.plugin == PLUGIN_NAME
        )


    def create_message_data(self) -> dict:
        result: dict = {
            ATTR_EVENT_MESSAGE: escape_markdown(self.payload.data.message),
        }
        
        if self.payload.data.feedback_items:
            result[ATTR_DATA] = {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD : ", ".join(
                    map(lambda x: " ".join([ f"{x.title}:/react", x.feedback, x.acknowledgement ]), 
                    self.payload.data.feedback_items)
                )
            }

        return result