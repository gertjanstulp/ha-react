from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.core import Event as HassEvent
from homeassistant.components.telegram_bot import (
    ATTR_CHAT_ID,
    ATTR_KEYBOARD_INLINE,
    ATTR_MESSAGE,
    ATTR_MESSAGEID,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_PLUGIN_PAYLOAD, REACT_ACTION_FEEDBACK_CONFIRM, REACT_TYPE_NOTIFY
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import Event, ReactionEvent, ReactionEventPayload
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.telegram.const import PLUGIN_NAME
from custom_components.react.plugin.telegram.telegram_api import TelegramApi


class TelegramNotifyFeedbackConfirmTask(DefaultReactionTask):
    def __init__(self, react: ReactBase, telegram_api: TelegramApi) -> None:
        super().__init__(react, TelegramNotifyFeedbackConfirmReactionEvent)
        self.telegram_api = telegram_api


    async def async_execute_default(self, action_event: TelegramNotifyFeedbackConfirmReactionEvent):
        self.react.log.debug("TelegramNotifyFeedbackConfirmTask: confirming feedback to telegram")
        await self.telegram_api.async_confirm_feedback(action_event.create_feedback_data(), action_event.context)


class TelegramNotifyFeedbackConfirmReactionEventPluginPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.chat_id: str = None
        self.message_id: str = None
        self.text: str = None

        self.load(source)


class TelegramNotifyFeedbackConfirmReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_PLUGIN_PAYLOAD: TelegramNotifyFeedbackConfirmReactionEventPluginPayload }

    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.plugin: str = None
        self.feedback: str = None
        self.acknowledgement: str = None
        self.plugin_payload: TelegramNotifyFeedbackConfirmReactionEventPluginPayload = None

        self.load(source)
        

class TelegramNotifyFeedbackConfirmReactionEvent(ReactionEvent[TelegramNotifyFeedbackConfirmReactionEventData]):
    
    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, TelegramNotifyFeedbackConfirmReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_FEEDBACK_CONFIRM and 
            self.payload.data.plugin == PLUGIN_NAME
        )


    def create_feedback_data(self) -> dict:
        return {
            ATTR_MESSAGEID: self.payload.data.plugin_payload.message_id,
            ATTR_CHAT_ID: self.payload.data.plugin_payload.chat_id,
            ATTR_MESSAGE: escape_markdown(f"{self.payload.data.plugin_payload.text} - {self.payload.data.acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
