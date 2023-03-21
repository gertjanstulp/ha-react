from __future__ import annotations

from homeassistant.components.light import SERVICE_TOGGLE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_LIGHT
from custom_components.react.plugin.light.api import Api
from custom_components.react.plugin.light.const import PLUGIN_NAME
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class LightToggleTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, LightToggleReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: LightToggleTask - {message}")


    async def async_execute_plugin(self, event: LightToggleReactionEvent):
        self._debug(f"Toggling light '{event.payload.entity}'")
        await self.api.async_light_toggle(event.context, event.payload.entity)
        

class LightToggleReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None

        self.load(source)


class LightToggleReactionEvent(ReactionEvent[LightToggleReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, LightToggleReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_LIGHT and
            self.payload.action == SERVICE_TOGGLE and 
            (not self.payload.data or
             (self.payload.data and (
              (not self.payload.data.plugin or 
               self.payload.data.plugin == PLUGIN_NAME))))
        )
