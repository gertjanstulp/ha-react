from __future__ import annotations

from homeassistant.components.fan import SERVICE_SET_PERCENTAGE
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_FAN
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.fan.api import FanApi
from custom_components.react.plugin.fan.config import FanConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class FanSetPercentageOutputBlock(OutputBlock[FanConfig], ApiType[FanApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, FanSetPercentageReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_FAN, 
            SERVICE_SET_PERCENTAGE,
        )]


    def log_event_caught(self, react_event: FanSetPercentageReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Fan set percentage reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: FanSetPercentageReactionEvent):
        if not (react_event.payload.data and
                react_event.payload.data.percentage is not None and
                react_event.payload.data.percentage >= 0 and 
                react_event.payload.data.percentage <= 100
        ):
            react_event.session.error(self.logger, "No valid percentage provided. Percentage should be a number between 0 and 100")
            return
        
        await self.api.async_fan_set_percentage(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.fan_provider,
            react_event.payload.data.percentage,
        )
        

class FanSetPercentageReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.fan_provider: str = None
        self.percentage: int = None

        self.load(source)


class FanSetPercentageReactionEvent(ReactionEvent[FanSetPercentageReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, FanSetPercentageReactionEventData)
