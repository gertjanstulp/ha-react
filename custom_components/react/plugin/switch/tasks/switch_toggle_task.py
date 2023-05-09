from __future__ import annotations

from homeassistant.components.switch import SERVICE_TOGGLE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_SWITCH
from custom_components.react.plugin.switch.api import SwitchApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class SwitchToggleTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: SwitchApi) -> None:
        super().__init__(react, SwitchToggleReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Switch plugin: SwitchToggleTask - {message}")


    async def async_execute_plugin(self, event: SwitchToggleReactionEvent):
        self._debug(f"Toggling switch '{event.payload.entity}'")
        await self.api.async_switch_toggle(
            event.context, 
            event.payload.entity, 
            event.payload.data.switch_provider if event.payload.data else None
        )
        

class SwitchToggleReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.switch_provider: str = None

        self.load(source)


class SwitchToggleReactionEvent(ReactionEvent[SwitchToggleReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, SwitchToggleReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_SWITCH and
            self.payload.action == SERVICE_TOGGLE
        )
