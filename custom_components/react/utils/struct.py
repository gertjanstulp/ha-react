
from datetime import datetime
from typing import Any, Union


from ..const import (
    ATTR_CONDITION,
    ATTR_FORWARD_ACTION,
    ATTR_OVERWRITE,
    ATTR_TIMING,
    REACTOR_TIMING_IMMEDIATE
)


class DynamicData():

    def __init__(self, source: dict = None) -> None:
        self.names: list[str] = []

        if not hasattr(self, "type_hints"):
            self.type_hints = {}

        if source:
            self.load(source)


    def load(self, source: dict) -> None:
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


    def get_flattened(self, key: str, default: Any = None) -> Any:
        result = self.get(key, default)
        if isinstance(result, MultiItem) and len(result) == 1:
            result = result.first
        return result


    def set(self, key: str, value: Any):
        if not key in self.names:
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


    def ensure(self, key: str, default: Any):
        if key in self.names: return

        if hasattr(self, key) and getattr(self, key, None) != None:
            self.names.append(key)
            return

        self.set(key, default)


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


    def __len__(self):
        return len(self.names)


    @property
    def first(self) -> Any:
        return self[0]


    def __getitem__(self, k):
        if self.any and len(self.names) > k:
            return self.get(self.names[k])
        return None

    
    def len(self):
        return len(self.names)


class CtorConfig(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.entity: Union[MultiItem, str] = None
        self.type: Union[MultiItem, str] = None
        self.action: Union[MultiItem, str] = None
        self.condition: str = None
        self.data: DynamicData = None



class CtorRuntime(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.entity: MultiItem = None
        self.type: MultiItem = None
        self.action: MultiItem = None
        self.condition: bool = None
        self.data: DynamicData = None
        
        self.ensure(ATTR_CONDITION, True)


class ScheduleData(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.at: datetime = None
        self.weekdays: MultiItem = None


class ActorConfig(CtorConfig):

    def __init__(self) -> None:
        super().__init__()


class ActorRuntime(CtorRuntime):

    def __init__(self) -> None:
        super().__init__()


class ReactorConfig(CtorConfig):

    def __init__(self) -> None:
        super().__init__()
        
        self.timing: str = None
        self.delay: Union[int, str] = None
        self.schedule: ScheduleData = None
        self.overwrite: Union[bool, str] = None
        self.reset_workflow: str = None
        self.forward_action: Union[bool, str] = None

        self.ensure(ATTR_TIMING, REACTOR_TIMING_IMMEDIATE)
        self.ensure(ATTR_OVERWRITE, False)
        self.ensure(ATTR_FORWARD_ACTION, False)


class ReactorRuntime(CtorRuntime):

    def __init__(self) -> None:
        super().__init__()

        self.timing: str = None
        self.delay: int = None
        self.schedule: ScheduleData = None
        self.overwrite: bool = None
        self.reset_workflow: str = None
        self.forward_action: bool = None

        self.ensure(ATTR_TIMING, REACTOR_TIMING_IMMEDIATE)
        self.ensure(ATTR_OVERWRITE, False)
        self.ensure(ATTR_FORWARD_ACTION, False)


