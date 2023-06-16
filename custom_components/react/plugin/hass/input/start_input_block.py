from homeassistant.const import EVENT_HOMEASSISTANT_START

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ACTION_START, 
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_TYPE, 
    ENTITY_HASS, 
    TYPE_SYSTEM,
)
from custom_components.react.tasks.filters import EVENT_TYPE_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent, HassEvent
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class HassEventStartInputBlock(InputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, HassEvent)
        self.track_event_filters = [EVENT_TYPE_FILTER_STRATEGY.get_filter(EVENT_HOMEASSISTANT_START)]


    def create_action_event_payloads(self, source_event: ReactEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"Hass start caught")
        return [{
            ATTR_ENTITY: ENTITY_HASS,
            ATTR_TYPE: TYPE_SYSTEM,
            ATTR_ACTION: ACTION_START,
        }]
    