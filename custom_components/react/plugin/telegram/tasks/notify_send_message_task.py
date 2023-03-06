from __future__ import annotations

from telegram.utils.helpers import escape_markdown

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_DATA, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE, 
    REACT_ACTION_SEND_MESSAGE, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.telegram.api import Api
from custom_components.react.plugin.telegram.const import (
    ATTR_SERVICE_DATA_INLINE_KEYBOARD, 
    PLUGIN_NAME
)

_LOGGER = get_react_logger()


class NotifySendMessageTask(PluginReactionTask):
    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, NotifySendMessageReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Telegram plugin: NotifySendMessageTask - {message}")


    async def async_execute_plugin(self, event: NotifySendMessageReactionEvent):
        self._debug("Sending message")
        await self.api.async_send_message(
            event.context,
            event.payload.entity,
            event.create_message_data(),
        )


class NotifySendMessageReactionEventFeedbackItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.title: str = None
        self.feedback: str = None
        self.acknowledgement: str = None

        self.load(source)


class NotifySendMessageReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: NotifySendMessageReactionEventFeedbackItem }

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.feedback_items: list[NotifySendMessageReactionEventFeedbackItem] = None

        self.load(source)


class NotifySendMessageReactionEvent(ReactionEvent[NotifySendMessageReactionEventData]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, NotifySendMessageReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_SEND_MESSAGE and
            self.payload.data and
            (not self.payload.data.plugin or self.payload.data.plugin == PLUGIN_NAME)
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