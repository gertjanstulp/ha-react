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
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_PLUGIN_PAYLOAD, 
    REACT_ACTION_CONFIRM_FEEDBACK, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.telegram.const import PLUGIN_NAME
from custom_components.react.plugin.telegram.api import Api

_LOGGER = get_react_logger()


class NotifyConfirmFeedbackTask(DefaultReactionTask):
    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, NotifyConfirmFeedbackReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Telegram plugin: NotifyConfirmFeedbackTask - {message}")


    async def async_execute_default(self, event: NotifyConfirmFeedbackReactionEvent):
        self._debug("Confirming feedback")
        await self.api.async_confirm_feedback(event.context, event.create_feedback_data())


class NotifyConfirmFeedbackReactionEventPluginPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.chat_id: str = None
        self.message_id: str = None
        self.text: str = None

        self.load(source)


class NotifyConfirmFeedbackReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_PLUGIN_PAYLOAD: NotifyConfirmFeedbackReactionEventPluginPayload }

    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.plugin: str = None
        self.feedback: str = None
        self.acknowledgement: str = None
        self.plugin_payload: NotifyConfirmFeedbackReactionEventPluginPayload = None

        self.load(source)
        

class NotifyConfirmFeedbackReactionEvent(ReactionEvent[NotifyConfirmFeedbackReactionEventData]):
    
    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, NotifyConfirmFeedbackReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_CONFIRM_FEEDBACK and 
            self.payload.data.plugin == PLUGIN_NAME
        )


    def create_feedback_data(self) -> dict:
        return {
            ATTR_MESSAGEID: self.payload.data.plugin_payload.message_id,
            ATTR_CHAT_ID: self.payload.data.plugin_payload.chat_id,
            ATTR_MESSAGE: escape_markdown(f"{self.payload.data.plugin_payload.text} - {self.payload.data.acknowledgement}"),
            ATTR_KEYBOARD_INLINE: None
        }
