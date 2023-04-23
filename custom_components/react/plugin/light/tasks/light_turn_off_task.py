from __future__ import annotations

from homeassistant.core import Event
from homeassistant.const import STATE_OFF

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_LIGHT
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class LightTurnOffTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: LightApi) -> None:
        super().__init__(react, LightTurnOffReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: LightTurnOffTask - {message}")


    async def async_execute_plugin(self, event: LightTurnOffReactionEvent):
        self._debug(f"Turning off light '{event.payload.entity}'")
        await self.api.async_light_turn_off(event.context, event.payload.entity, event.payload.data.light_provider_name if event.payload.data else None)
        

class LightTurnOffReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.light_provider_name: str = None

        self.load(source)


class LightTurnOffReactionEvent(ReactionEvent[LightTurnOffReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, LightTurnOffReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_LIGHT and
            self.payload.action == STATE_OFF
        )
