from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    REACT_ACTION_TRIGGER, 
    REACT_TYPE_ALARM_CONTROL_PANEL
)
from custom_components.react.plugin.alarm_control_panel.api import AlarmApi
from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig
from custom_components.react.plugin.base import ApiType
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class AlarmTriggerOutputBlock(OutputBlock[AlarmConfig], ApiType[AlarmApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, AlarmTriggerReactionEvent)
        
        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_ALARM_CONTROL_PANEL, 
            REACT_ACTION_TRIGGER
        )]


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm_control_panel plugin: AlarmTriggerOutputBlock - {message}")


    async def async_handle_event(self, react_event: AlarmTriggerReactionEvent):
        self._debug(f"Triggering '{react_event.payload.entity}'")
        await self.api.async_alarm_trigger(
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.alarm_control_panel_provider if react_event.payload.data else None
        )
        

class AlarmTriggerReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.alarm_control_panel_provider: str = None

        self.load(source)


class AlarmTriggerReactionEvent(ReactionEvent[AlarmTriggerReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, AlarmTriggerReactionEventData)
