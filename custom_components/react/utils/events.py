from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from homeassistant.core import Event as HassEvent
from custom_components.react.const import ATTR_ACTION, ATTR_DATA, ATTR_ENTITY, ATTR_TYPE

from custom_components.react.utils.struct import DynamicData

T_payload = TypeVar('T_payload', bound=DynamicData)
T_data = TypeVar('T_data', bound=DynamicData)


class Event(Generic[T_payload]):
    
    def __init__(self, hass_event: HassEvent, t_payload_type: Type[T_payload] = DynamicData, *t_payload_args: Any) -> None:
        self.context = hass_event.context
        self.event_type = hass_event.event_type

        self.payload: T_payload = t_payload_type(*t_payload_args)
        self.payload.load(hass_event.data)


    @property
    def applies(self) -> bool:
        raise NotImplementedError()


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


class ActionEvent(Event[T_payload], Generic[T_payload]):

    def __init__(self, hass_event: HassEvent, t_payload_type: Type[T_payload] = ActionEventPayload) -> None:
        super().__init__(hass_event, t_payload_type)


########## Reaction event ##########


class ReactionEventPayload(ReactEventPayload[T_data], Generic[T_data]):
    def __init__(self, t_dd_type: Type[T_data] = DynamicData) -> None:
        super().__init__(t_dd_type)
        self.reactor_id: str = None


class ReactionEvent(Event[ReactionEventPayload[T_data]], Generic[T_data]):
    def __init__(self, hass_event: HassEvent, t_data_type: Type[T_data] = DynamicData) -> None:
        super().__init__(hass_event, ReactionEventPayload, t_data_type)
