from __future__ import annotations

from homeassistant.core import Event as HaEvent
from homeassistant.const import STATE_ON

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_LIGHT
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class LightTurnOnOutputBlock(OutputBlock[LightConfig], ApiType[LightApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, LightTurnOnReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_LIGHT, 
            STATE_ON,
        )]


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: LightTurnOnOutputBlock - {message}")


    async def async_handle_event(self, react_event: LightTurnOnReactionEvent):
        self._debug(f"Turning on light '{react_event.payload.entity}'")
        await self.api.async_light_turn_on(
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.light_provider if react_event.payload.data else None
        )
        

class LightTurnOnReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.light_provider: str = None

        self.load(source)


class LightTurnOnReactionEvent(ReactionEvent[LightTurnOnReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, LightTurnOnReactionEventData)
