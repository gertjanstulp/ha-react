from __future__ import annotations
from datetime import datetime

from typing import Any, Generic, Type, TypeVar

from homeassistant.const import (
    ATTR_DOMAIN,
    ATTR_ENTITY_ID, 
    ATTR_STATE,
)
from homeassistant.core import Event as HaEvent, split_entity_id, State

from custom_components.react.const import ATTR_ACTION, ATTR_DATA, ATTR_ENTITY, ATTR_LAST_CHANGED, ATTR_NEW_STATE, ATTR_OBJECT_ID, ATTR_OLD_STATE, ATTR_TYPE
from custom_components.react.utils.struct import DynamicData

T_payload = TypeVar('T_payload', bound=DynamicData)
T_data = TypeVar('T_data', bound=DynamicData)


class ReactEvent(Generic[T_payload]):
    
    def __init__(self, ha_event: HaEvent, t_payload_type: Type[T_payload] = DynamicData, *t_payload_args: Any) -> None:
        self.context = ha_event.context
        self.event_type = ha_event.event_type

        self.payload: T_payload = t_payload_type(*t_payload_args)
        self.payload.load(ha_event.data)


    @property
    def applies(self) -> bool:
        return True


class ReactEventPayload(DynamicData, Generic[T_data]):

    def __init__(self, t_dd_type: Type[T_data] = DynamicData) -> None:
        super().__init__()
        
        self.type_hints: dict = {ATTR_DATA: t_dd_type}

        self.entity: str = None
        self.type: str = None
        self.action: str = None
        self.data: T_data = None

        self.ensure(ATTR_ENTITY, None)
        self.ensure(ATTR_TYPE, None)
        self.ensure(ATTR_ACTION, None)
        self.ensure(ATTR_DATA, None)


    def load(self, source: dict) -> None:
        super().load(source)


########## Action event ##########


class ActionEventPayload(ReactEventPayload[T_data], Generic[T_data]):
    def __init__(self, t_dd_type: Type[T_data] = DynamicData) -> None:
        super().__init__(t_dd_type)


    def load(self, source: dict) -> None:
        super().load(source)
        self.ensure(ATTR_DATA, None)


class ActionEvent(ReactEvent[T_payload], Generic[T_payload]):

    def __init__(self, ha_event: HaEvent, t_payload_type: Type[T_payload] = ActionEventPayload) -> None:
        super().__init__(ha_event, t_payload_type)


########## Reaction event ##########


class ReactionEventPayload(ReactEventPayload[T_data], Generic[T_data]):
    def __init__(self, t_dd_type: Type[T_data] = DynamicData) -> None:
        super().__init__(t_dd_type)
        self.reactor_id: str = None


class ReactionEvent(ReactEvent[ReactionEventPayload[T_data]], Generic[T_data]):
    def __init__(self, ha_event: HaEvent, t_data_type: Type[T_data] = DynamicData) -> None:
        super().__init__(ha_event, ReactionEventPayload, t_data_type)


########## StateChanged event ##########


class StateChangedEventPayloadState(DynamicData):
    def __init__(self, source: State = None) -> None:
        super().__init__()

        self.entity_id: str = None
        self.state: str = None
        self.domain: str = None
        self.object_id: str = None
        self.last_changed: datetime = None

        self.set(ATTR_ENTITY_ID, source.entity_id)
        self.set(ATTR_STATE, source.state)
        self.set(ATTR_DOMAIN, source.domain)
        self.set(ATTR_OBJECT_ID, source.object_id)
        self.set(ATTR_LAST_CHANGED, source.last_changed)

        # self.load(source)

        # if self.entity_id:
        #     parts = split_entity_id(self.entity_id)
        #     self.domain = parts[0]
        #     self.object_id = parts[1]

    
class StateChangedEventPayload(DynamicData):

    def __init__(self) -> None:
        super().__init__()
        
        self.entity_id: str = None
        self.old_state: StateChangedEventPayloadState = None
        self.new_state: StateChangedEventPayloadState = None


    def load(self, source: dict | DynamicData) -> None:
        self.entity_id = source.get(ATTR_ENTITY_ID, None)

        old_state = source.get(ATTR_OLD_STATE, None)
        new_state = source.get(ATTR_NEW_STATE, None)

        self.old_state = StateChangedEventPayloadState(old_state) if old_state else None
        self.new_state = StateChangedEventPayloadState(new_state) if new_state else None
        
            
class StateChangedEvent(ReactEvent[StateChangedEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, StateChangedEventPayload)


########## Hass event ##########


class HassEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)


class HassEvent(ReactEvent[HassEventPayload]):
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, HassEventPayload)


########## Time event ##########


class TimeEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)


class TimeEvent(ReactEvent[TimeEventPayload]):
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, TimeEventPayload)
