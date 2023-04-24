from __future__ import annotations

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEMS, 
    REACT_ACTION_SEND_MESSAGE, 
    REACT_TYPE_NOTIFY
)

from custom_components.react.plugin.notify.api import NotifyApi
from custom_components.react.plugin.notify.const import FeedbackItem

_LOGGER = get_react_logger()


class NotifySendMessageTask(PluginReactionTask):
    def __init__(self, react: ReactBase, api: NotifyApi) -> None:
        super().__init__(react, NotifySendMessageReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Notify plugin: NotifySendMessageTask - {message}")


    async def async_execute_plugin(self, event: NotifySendMessageReactionEvent):
        self._debug("Sending message")
        await self.api.async_send_message(
            event.context,
            event.payload.entity,
            event.payload.data.message if event.payload.data else None,
            event.payload.data.feedback_items if event.payload.data else None,
            event.payload.data.notify_provider if event.payload.data else None,
        )


class NotifySendMessageReactionEventData(DynamicData):
    type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: FeedbackItem }

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.message: str = None
        self.feedback_items: list[FeedbackItem] = None
        self.notify_provider: str = None

        self.load(source)


class NotifySendMessageReactionEvent(ReactionEvent[NotifySendMessageReactionEventData]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, NotifySendMessageReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_SEND_MESSAGE and
            self.payload.data
        )
