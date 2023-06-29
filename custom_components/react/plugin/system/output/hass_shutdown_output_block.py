from __future__ import annotations

from homeassistant.const import SERVICE_HOMEASSISTANT_RESTART
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_SYSTEM
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.system.api import SystemApi
from custom_components.react.plugin.system.config import SystemConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class SystemHassShutdownOutputBlock(OutputBlock[SystemConfig], ApiType[SystemApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, HassShutdownReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_SYSTEM, 
            SERVICE_HOMEASSISTANT_RESTART,
        )]


    async def async_handle_event(self, react_event: HassShutdownReactionEvent):
        react_event.session.debug(self.logger, f"HomeAssistant shutdown reaction caught")
        await self.api.async_system_restart(
            react_event.session,
            react_event.context, 
            react_event.payload.data.system_provider if react_event.payload.data else None
        )
        

class HassShutdownReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        self.system_provider: str = None
        self.load(source)


class HassShutdownReactionEvent(ReactionEvent[HassShutdownReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, HassShutdownReactionEventData)
