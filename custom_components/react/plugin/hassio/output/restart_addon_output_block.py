from __future__ import annotations

from homeassistant.components.hassio import SERVICE_ADDON_RESTART
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_HASSIO
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.hassio.api import HassioApi
from custom_components.react.plugin.hassio.config import HassioConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class HassioRestartAddonOutputBlock(OutputBlock[HassioConfig], ApiType[HassioApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, HassioRestartAddonReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_HASSIO, 
            SERVICE_ADDON_RESTART,
        )]


    async def async_handle_event(self, react_event: HassioRestartAddonReactionEvent):
        react_event.session.debug(self.logger, f"Hassio restart addon reaction caught: '{react_event.payload.entity}'")
        await self.api.async_hassio_restart_addon(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.hassio_provider if react_event.payload.data else None)


class HassioRestartAddonReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.hassio_provider: str = None

        self.load(source)


class HassioRestartAddonReactionEvent(ReactionEvent[HassioRestartAddonReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, HassioRestartAddonReactionEventData)
