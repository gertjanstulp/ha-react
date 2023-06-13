from __future__ import annotations

from homeassistant.components.fan import SERVICE_DECREASE_SPEED
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


class FanDecreaseSpeedOutputBlock(OutputBlock[FanConfig], ApiType[FanApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, FanDecreaseSpeedReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_FAN, 
            SERVICE_DECREASE_SPEED,
        )]


    def log_event_caught(self, react_event: FanDecreaseSpeedReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Fan decrease speed reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: FanDecreaseSpeedReactionEvent):
        if (react_event.payload.data and
            react_event.payload.data.percentage_step is not None and
            (react_event.payload.data.percentage_step < 0 or 
             react_event.payload.data.percentage_step > 100)
        ):
            react_event.session.error(self.logger, "Invalid percentage step provided. Percentage step should be a number between 0 and 100")
            return
        
        await self.api.async_fan_decrease_speed(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.fan_provider if react_event.payload.data else None,
            react_event.payload.data.percentage_step if react_event.payload.data else None,
        )
        

class FanDecreaseSpeedReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.fan_provider: str = None
        self.percentage_step: int = None

        self.load(source)


class FanDecreaseSpeedReactionEvent(ReactionEvent[FanDecreaseSpeedReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, FanDecreaseSpeedReactionEventData)
