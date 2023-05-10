from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
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


class NotifySendMessageOutputBlock(OutputBlock[NotifyConfig], ApiType[NotifyApi]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, NotifySendMessageReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_NOTIFY, 
            REACT_ACTION_SEND_MESSAGE,
        )]


    def _debug(self, message: str):
        _LOGGER.debug(f"Notify plugin: NotifySendMessageOutputBlock - {message}")


    async def async_handle_event(self, react_event: NotifySendMessageReactionEvent):
        self._debug("Sending message")
        await self.api.async_send_message(
            react_event.context,
            react_event.payload.entity,
            react_event.payload.data.message if react_event.payload.data else None,
            react_event.payload.data.feedback_items if react_event.payload.data else None,
            react_event.payload.data.notify_provider if react_event.payload.data else None,
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

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, NotifySendMessageReactionEventData)


    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_NOTIFY and
            self.payload.action == REACT_ACTION_SEND_MESSAGE and
            self.payload.data
        )
