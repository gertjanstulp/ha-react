from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    REACT_ACTION_ARM_HOME, 
    REACT_TYPE_ALARM
)
from custom_components.react.plugin.alarm.api import AlarmApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class AlarmArmHomeTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: AlarmApi) -> None:
        super().__init__(react, AlarmArmHomeReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm plugin: AlarmArmHomeTask - {message}")


    async def async_execute_plugin(self, event: AlarmArmHomeReactionEvent):
        self._debug(f"Arming home '{event.payload.entity}'")
        await self.api.async_alarm_arm_home(
            event.context, 
            event.payload.entity,
            event.payload.data.alarm_provider if event.payload.data else None
        )
        

class AlarmArmHomeReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.alarm_provider: str = None

        self.load(source)


class AlarmArmHomeReactionEvent(ReactionEvent[AlarmArmHomeReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, AlarmArmHomeReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_ALARM and
            self.payload.action == REACT_ACTION_ARM_HOME
        )
