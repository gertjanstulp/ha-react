from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_EVENT, 
    ATTR_TYPE, 
    REACT_TYPE_BUTTON,
)
from custom_components.react.plugin.deconz.config import DeconzConfig
from custom_components.react.plugin.deconz.const import EVENT_DECONZ_EVENT
from custom_components.react.tasks.filters import EVENT_TYPE_AND_DATA_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.struct import DynamicData


class DeconzButtonInputBlock(InputBlock[DeconzConfig]):
    def __init__(self, react: ReactBase, deconz_code: str, react_action: str) -> None:
        super().__init__(react, DeconzButtonEvent)
        self.react_action = react_action
        match_data = {
            ATTR_EVENT: deconz_code
        }
        self.track_event_filter = EVENT_TYPE_AND_DATA_FILTER_STRATEGY.get_filter(EVENT_DECONZ_EVENT, match_data)


    def load(self):
        super().load()
        self.entity_maps = self.plugin.config.entity_maps if self.plugin.config.entity_maps else DynamicData()


    def create_action_event_payloads(self, source_event: DeconzButtonEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"Deconz short press event caught: device id '{source_event.payload.device_id}'")
        entity_id = self.entity_maps.get(source_event.payload.device_id, source_event.payload.device_id)
        return [{
            ATTR_ENTITY: entity_id,
            ATTR_TYPE: REACT_TYPE_BUTTON,
            ATTR_ACTION: self.react_action        
        }]


class DeconzButtonEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.event: str = None
        self.load(source)
        
            
class DeconzButtonEvent(ReactEvent[DeconzButtonEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, DeconzButtonEventPayload)
