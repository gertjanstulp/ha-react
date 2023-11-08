from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_TYPE, 
    REACT_TYPE_BUTTON,
)
from custom_components.react.plugin.mqtt.config import MqttConfig
from custom_components.react.tasks.filters import ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY, track_key
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.struct import DynamicData


class MqttButtonInputBlock(InputBlock[MqttConfig]):
    def __init__(self, react: ReactBase, mqtt_button_action: str, react_action: str, event_description: str) -> None:
        super().__init__(react, MqttButtonEvent)
        self.mqtt_button_action = mqtt_button_action
        self.react_action = react_action
        self.event_description = event_description
        
        self.entity_track_keys: list[str] = []
        self.mapped_entity_ids: dict[str, str] = {}


    def load(self):
        super().load()
        self.entity_maps = self.plugin.config.entity_maps if self.plugin.config.entity_maps else []
        for entity_map in (item for item in self.entity_maps if self.mqtt_button_action in item):
            self.mapped_entity_ids[entity_map.entity_id] = entity_map.mapped_entity_id
            entity_track_key = track_key(self.__class__.__name__, entity_map.entity_id)
            filter = ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY.get_filter(entity_map.entity_id, track_key=entity_track_key, old_state=entity_map.get(self.mqtt_button_action), new_state="")
            self.manager.track_state_change(filter, self)
            self.entity_track_keys.append(entity_track_key)


    def unload(self):
        super().unload()
        for entity_track_key in self.entity_track_keys:
            self.manager.untrack_key(self, entity_track_key)
        self.entity_track_keys.clear()


    def create_action_event_payloads(self, source_event: MqttButtonEvent) -> list[dict]:
        entity_id = self.mapped_entity_ids.get(source_event.payload.entity_id, source_event.payload.entity_id)
        source_event.session.debug(self.logger, f"Mqtt {self.event_description} event caught: entity id {source_event.payload.entity_id} mapped to {entity_id}")
        return [{
            ATTR_ENTITY: entity_id,
            ATTR_TYPE: REACT_TYPE_BUTTON,
            ATTR_ACTION: self.react_action        
        }]


class MqttButtonEventPayloadState(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.state: str = None
        self.load(source)


class MqttButtonEventPayload(DynamicData):

    type_hints: dict = {
        ATTR_OLD_STATE: MqttButtonEventPayloadState,
        ATTR_NEW_STATE: MqttButtonEventPayloadState,
    }


    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.entity_id: str = None
        self.old_state: MqttButtonEventPayloadState = None
        self.new_state: MqttButtonEventPayloadState = None
        self.load(source)
        
            
class MqttButtonEvent(ReactEvent[MqttButtonEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MqttButtonEventPayload)
