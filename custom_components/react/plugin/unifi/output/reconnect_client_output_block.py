from __future__ import annotations

from homeassistant.components.unifi.services import SERVICE_RECONNECT_CLIENT
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_UNIFI
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.unifi.api import UnifiApi
from custom_components.react.plugin.unifi.config import UnifiConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class UnifiReconnectClientOutputBlock(OutputBlock[UnifiConfig], ApiType[UnifiApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, UnifiReconnectClientReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_UNIFI, 
            SERVICE_RECONNECT_CLIENT,
        )]


    async def async_handle_event(self, react_event: UnifiReconnectClientReactionEvent):
        react_event.session.debug(self.logger, f"Unifi reconnect client reaction caught: '{react_event.payload.entity}'")
        await self.api.async_unifi_reconnect_client(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.unifi_provider if react_event.payload.data else None)


class UnifiReconnectClientReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.unifi_provider: str = None

        self.load(source)


class UnifiReconnectClientReactionEvent(ReactionEvent[UnifiReconnectClientReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, UnifiReconnectClientReactionEventData)
