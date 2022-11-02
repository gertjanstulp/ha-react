
from typing import Generic, Type, TypeVar
from homeassistant.core import Event
from custom_components.react.const import ATTR_DATA

from custom_components.react.utils.struct import DynamicData

T_d = TypeVar('T_d', bound=DynamicData)
T_dd = TypeVar('T_dd', bound=DynamicData)


class ReactEvent(Generic[T_d]):
    
    def __init__(self, event: Event, t_d_type: Type[T_d] = DynamicData) -> None:
        self.context = event.context
        self.event_type = event.event_type

        self.data: T_d = t_d_type()
        self.data.load(event.data)


    @property
    def applies(self) -> bool:
        raise NotImplementedError()


class CtionEventData(DynamicData, Generic[T_dd]):

    def __init__(self, t_dd_type: Type[T_dd] = DynamicData) -> None:
        super().__init__()
        
        self.type_hints: dict = {ATTR_DATA: t_dd_type}

        self.entity: str = None
        self.type: str = None
        self.action: str = None
        self.data: T_dd = None


    def load(self, source: dict) -> None:
        super().load(source)


class ActionEventData(CtionEventData[T_dd], Generic[T_dd]):
    def __init__(self, t_dd_type: Type[T_dd] = DynamicData) -> None:
        super().__init__(t_dd_type)


    def load(self, source: dict) -> None:
        super().load(source)
        self.ensure(ATTR_DATA, None)
        

class ReactionEventData(CtionEventData[T_dd], Generic[T_dd]):
    def __init__(self, t_dd_type: Type[T_dd] = DynamicData) -> None:
        super().__init__(t_dd_type)
        self.reactor_id: str = None


class ActionEvent(ReactEvent[ActionEventData[DynamicData]]):

    def __init__(self, event: Event) -> None:
        super().__init__(event, ActionEventData)


class ReactionEvent(ReactEvent[T_d], Generic[T_d]):

    def __init__(self, event: Event, t_d_type: Type[T_d] = ReactionEventData) -> None:
        super().__init__(event, t_d_type)
