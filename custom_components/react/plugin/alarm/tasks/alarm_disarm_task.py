from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    REACT_ACTION_DISARM, 
    REACT_TYPE_ALARM
)
from custom_components.react.plugin.alarm.api import AlarmApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class AlarmDisarmTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: AlarmApi) -> None:
        super().__init__(react, AlarmDisarmReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm plugin: AlarmDisarmTask - {message}")


    async def async_execute_plugin(self, event: AlarmDisarmReactionEvent):
        self._debug(f"Disarmning '{event.payload.entity}'")
        
        if not self.api.verify_config():
            return
        
        await self.api.async_alarm_disarm(event.context, event.payload.entity, event.payload.data.alarm_provider_name if event.payload.data else None)
        

class AlarmDisarmReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.alarm_provider_name: str = None

        self.load(source)


class AlarmDisarmReactionEvent(ReactionEvent[AlarmDisarmReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, AlarmDisarmReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_ALARM and
            self.payload.action == REACT_ACTION_DISARM
        )
