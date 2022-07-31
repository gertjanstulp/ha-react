
from datetime import datetime
from typing import Any, Union

from ..const import (
    REACTOR_TIMING_IMMEDIATE
)


class DynamicData():
    def __init__(self, source: dict = None) -> None:
        self.names: list[str] = []

        if not hasattr(self, "type_hints"):
            self.type_hints = {}

        if not source: return
        
        for k,v in source.items():
            self.set(k, v)


    def type_hint(self, key):
        return self.type_hints.get(key, DynamicData)


    @property
    def has_data(self) -> bool:
        return len(self.names) > 0


    def get(self, key: str, default: Any = None) -> Any:
        if key in self.names:
            return getattr(self, key)
        else:
            return default


    def set(self, key: str, value: Any):
        self.names.append(key)
        if isinstance(value, (MultiItem, DynamicData)):
            setattr(self, key, value)
        elif isinstance(value, dict):
            setattr(self, key, self.type_hint(key)(value))
        elif isinstance(value, list):
            if isinstance(value[0], dict):
                items = []
                for item in value:
                    items.append(self.type_hint(key)(item))
                setattr(self, key, items)
            elif isinstance(value[0], DynamicData):
                setattr(self, key, value)
            else:
                setattr(self, key, MultiItem( {f"_{index}":item for index,item in enumerate(value)} ))
        else:
            setattr(self, key, value)


    def as_dict(self) -> dict:
        result = {}

        for name in self.names:
            v = getattr(self, name)
            if isinstance(v, DynamicData) and v.has_data:
                result[name] = v.as_dict()
            elif isinstance(v, list):
                if isinstance(v[0], DynamicData):
                    result[name] = [ x.as_dict() for x in v ]
                else:
                    result[name] = v
            else:
                result[name] = v
        
        return result
    

    @property
    def any(self) -> bool:
        return len(self.names) > 0


class MultiItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)

    class MultiItemIterator:
        def __init__(self, parent: Any, names: list[str]):
            self.parent = parent
            self.names = names
            self.num = 0
            self.end = len(names) - 1


        def __next__(self):
            if self.num > self.end:
                raise StopIteration
            else:
                result = getattr(self.parent, self.names[self.num])
                self.num += 1
                return result


    def as_dict(self):
        return [getattr(self, name) for name in self.names]


    def __iter__(self):
        return MultiItem.MultiItemIterator(self, self.names)


    @property
    def first(self) -> Any:
        if self.any:
            return self.get(self.names[0])
        return None


class CtorData(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)

    entity: Union[MultiItem, str] = None
    type: Union[MultiItem, str] = None
    action: Union[MultiItem, str] = None
    condition: Union[bool, str] = True
    data: DynamicData = DynamicData(None)


class ScheduleData(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)


    at: datetime = None
    weekdays: MultiItem = None


class ActorData(CtorData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)


class ReactorData(CtorData):
    def __init__(self, source: dict = None) -> None:
        super().__init__(source)

    timing: str = REACTOR_TIMING_IMMEDIATE
    delay: Union[int, str] = None
    schedule: ScheduleData = None
    overwrite: Union[bool, str] = False
    reset_workflow: str = None
    forward_action: Union[bool, str] = False
