from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_RESET_TEMPERATURE, REACT_ACTION_SET_TEMPERATURE, REACT_TYPE_CLIMATE
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.climate.api import ClimateApi
from custom_components.react.plugin.climate.config import ClimateConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class ClimateResetTemperatureOutputBlock(OutputBlock[ClimateConfig], ApiType[ClimateApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, ClimateResetTemperatureReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_CLIMATE, 
            REACT_ACTION_RESET_TEMPERATURE
        )]


    async def async_handle_event(self, react_event: ClimateResetTemperatureReactionEvent):
        react_event.session.debug(self.logger, f"Climate reset_temperature reaction caught: '{react_event.payload.entity}'")
        await self.api.async_reset_temperature(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.climate_provider if react_event.payload.data else None)
        

class ClimateResetTemperatureReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.climate_provider: str = None

        self.load(source)


class ClimateResetTemperatureReactionEvent(ReactionEvent[ClimateResetTemperatureReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, ClimateResetTemperatureReactionEventData)
        