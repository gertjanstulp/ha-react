from __future__ import annotations

from homeassistant.core import Event as HaEvent
from homeassistant.const import STATE_OFF

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_LIGHT
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class LightTurnOffOutputBlock(OutputBlock[LightConfig], ApiType[LightApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, LightTurnOffReactionEvent)
        
        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_LIGHT, 
            STATE_OFF,
        )]


    async def async_handle_event(self, react_event: LightTurnOffReactionEvent):
        react_event.session.debug(self.logger, f"Light turn off reaction caught: '{react_event.payload.entity}'")
        await self.api.async_light_turn_off(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.light_provider if react_event.payload.data else None
        )
        

class LightTurnOffReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.light_provider: str = None

        self.load(source)


class LightTurnOffReactionEvent(ReactionEvent[LightTurnOffReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, LightTurnOffReactionEventData)
