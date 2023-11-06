from __future__ import annotations

from homeassistant.const import (
    EVENT_STATE_CHANGED,
)
from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_EVENT,
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_STATE, 
    ATTR_TYPE, 
    REACT_TYPE_BUTTON,
)
from custom_components.react.plugin.mqtt.config import MqttConfig
from custom_components.react.tasks.filters import EVENT_TYPE_AND_DATA_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent, StateChangedEventPayload
from custom_components.react.utils.struct import DynamicData


class MqttButtonInputBlock(InputBlock[MqttConfig]):
    def __init__(self, react: ReactBase, mqtt_button_state: str, react_action: str, event_description: str) -> None:
        super().__init__(react, MqttButtonEvent)
        self.react_action = react_action
        self.event_description = event_description
        match_data = {
            ATTR_OLD_STATE: {
                ATTR_STATE: mqtt_button_state
            },
            ATTR_NEW_STATE: {
                ATTR_STATE: ""
            }
        }
        self.track_event_filter = EVENT_TYPE_AND_DATA_FILTER_STRATEGY.get_filter(EVENT_STATE_CHANGED, match_data)


    def load(self):
        super().load()
        self.entity_maps = self.plugin.config.entity_maps if self.plugin.config.entity_maps else DynamicData()


    def create_action_event_payloads(self, source_event: MqttButtonEvent) -> list[dict]:
        entity_id = self.entity_maps.get(source_event.payload.entity_id, source_event.payload.entity_id)
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
