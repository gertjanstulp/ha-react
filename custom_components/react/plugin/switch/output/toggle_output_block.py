from __future__ import annotations

from homeassistant.components.switch import SERVICE_TOGGLE
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_SWITCH
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.plugin.switch.api import SwitchApi
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class SwitchToggleOutputBlock(OutputBlock[LightConfig], ApiType[SwitchApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, SwitchToggleReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_SWITCH, 
            SERVICE_TOGGLE
        )]


    def _debug(self, message: str):
        _LOGGER.debug(f"Switch plugin: SwitchToggleOutputBlock - {message}")


    async def async_handle_event(self, react_event: SwitchToggleReactionEvent):
        self._debug(f"Toggling switch '{react_event.payload.entity}'")
        await self.api.async_switch_toggle(
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.switch_provider if react_event.payload.data else None
        )
        

class SwitchToggleReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.switch_provider: str = None

        self.load(source)


class SwitchToggleReactionEvent(ReactionEvent[SwitchToggleReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, SwitchToggleReactionEventData)
