from __future__ import annotations
from datetime import datetime

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    REACT_ACTION_LOG, 
    REACT_TYPE_STATE,
)
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.state.api import StateApi
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData, StateConfig


class TrackStateOutputBlock(OutputBlock[StateConfig], ApiType[StateApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, TrackStateReactionEvent)
        
        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_STATE, 
            REACT_ACTION_LOG
        )]


    def log_event_caught(self, react_event: TrackStateReactionEvent) -> None:
        react_event.session.debug(self.logger, f"State track state reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: TrackStateReactionEvent):
        await self.api.async_track_entity_state_change(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.old_state if react_event.payload.data else None, 
            react_event.payload.data.new_state if react_event.payload.data else None,
            react_event.payload.data.timestamp if react_event.payload.data else None,
            react_event.payload.data.state_provider if react_event.payload.data else None,
        )


class TrackStateReactionEventPayload(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.state_provider: str = None
        self.old_state: str = None
        self.new_state: str = None
        self.timestamp: datetime = None
        self.load(source)


class TrackStateReactionEvent(ReactionEvent[TrackStateReactionEventPayload]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, TrackStateReactionEventPayload)
