from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    REACT_ACTION_ARM_NIGHT, 
    REACT_TYPE_ALARM_CONTROL_PANEL
)
from custom_components.react.plugin.alarm_control_panel.api import AlarmApi
from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig
from custom_components.react.plugin.base import ApiType
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class AlarmArmNightOutputBlock(OutputBlock[AlarmConfig], ApiType[AlarmApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, AlarmArmNightReactionEvent)
        
        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_ALARM_CONTROL_PANEL, 
            REACT_ACTION_ARM_NIGHT
        )]


    async def async_handle_event(self, react_event: AlarmArmNightReactionEvent):
        react_event.session.debug(self.logger, f"Alarm arm night reaction caught: '{react_event.payload.entity}'")
        await self.api.async_alarm_arm_night(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.alarm_control_panel_provider if react_event.payload.data else None
        )
        

class AlarmArmNightReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.alarm_control_panel_provider: str = None

        self.load(source)


class AlarmArmNightReactionEvent(ReactionEvent[AlarmArmNightReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, AlarmArmNightReactionEventData)
