from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_TYPE, 
)
from custom_components.react.plugin.esphome.config import EspHomeConfig
from custom_components.react.plugin.esphome.const import EVENT_ESPHOME_EVENT
from custom_components.react.tasks.filters import EVENT_TYPE_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.struct import DynamicData


class EspHomeEventInputBlock(InputBlock[EspHomeConfig]):
    def __init__(self, react: ReactBase, entity_property: str = None, react_type: str = None, esphome_event_name: str = None, react_action: str = None) -> None:
        super().__init__(react, EspHomeEventActionEvent)
        self.entity_property = entity_property
        self.react_type = react_type
        self.esphome_event_name= esphome_event_name
        self.react_action = react_action
        self.track_event_filter = EVENT_TYPE_FILTER_STRATEGY.get_filter(f"{EVENT_ESPHOME_EVENT}{esphome_event_name}")


    def create_action_event_payloads(self, source_event: EspHomeEventActionEvent) -> list[dict]:
        entity = source_event.payload.get(self.entity_property, None)
        source_event.session.debug(self.logger, f"EspHome event caught: '{self.esphome_event_name}' event from {self.react_type}.{entity}")
        return [{
            ATTR_ENTITY: entity,
            ATTR_TYPE: self.react_type,
            ATTR_ACTION: self.react_action
        }]


class EspHomeEventActionEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.load(source)
        
            
class EspHomeEventActionEvent(ReactEvent[EspHomeEventActionEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, EspHomeEventActionEventPayload)
