from __future__ import annotations

from homeassistant.core import Event
from homeassistant.const import STATE_ON

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_LIGHT
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.plugin.light.const import PLUGIN_NAME
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class LightTurnOnTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: LightApi) -> None:
        super().__init__(react, LightTurnOnReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: LightTurnOnTask - {message}")


    async def async_execute_plugin(self, event: LightTurnOnReactionEvent):
        self._debug(f"Turning on light '{event.payload.entity}'")
        await self.api.async_light_turn_on(event.context, event.payload.entity)
        

class LightTurnOnReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None

        self.load(source)


class LightTurnOnReactionEvent(ReactionEvent[LightTurnOnReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, LightTurnOnReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_LIGHT and
            self.payload.action == STATE_ON and 
            (not self.payload.data or
             (self.payload.data and (
              (not self.payload.data.plugin or 
               self.payload.data.plugin == PLUGIN_NAME))))
        )
