from __future__ import annotations

from datetime import datetime
from typing import Any, Union

from homeassistant.helpers.template import Template

from ..const import (
    ATTR_CONDITION,
    ATTR_DELAY,
    ATTR_FORWARD_ACTION,
    ATTR_FORWARD_DATA,
    ATTR_OVERWRITE,
    ATTR_SCHEDULE,
    ATTR_STATE,
    ATTR_WAIT,
    PROP_TYPE_DEFAULT,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
    RESTART_MODE_ABORT,
)


class DynamicData():

    def __init__(self, source: dict = None) -> None:
        self._keys: list[str] = []
        self._prop_types: dict[str, str] = {}
        self._templates: dict[str, str] = {}

        if not hasattr(self, "type_hints"):
            self.type_hints = {}

        if source:
            self.load(source)

        self.source = source


    def __contains__(self, key):
        return key in self._keys


    def keys(self):
        return self._keys

    # def items(self):
    #     for name in self._keys:
    #         yield self.get(name)


    def load(self, source: Union[dict, DynamicData]) -> None:
        if not source:
            return
        for key in source.keys():
            self.set(key, source.get(key))


    def type_hint(self, key):
        return self.type_hints.get(key, DynamicData)


    @property
    def has_data(self) -> bool:
        return len(self._keys) > 0


    def get(self, key: str, default: Any = None) -> Any:
        if key in self._keys:
            return getattr(self, key)
        else:
            return default


    def get_flattened(self, key: str, default: Any = None) -> Any:
        result = self.get(key, default)
        if isinstance(result, MultiItem) and len(result) == 1:
            result = result.first
        elif isinstance(result, list) and len(result) == 1:
            result = result[0]
        return result


    def set_type(self, key: str, prop_type: str = PROP_TYPE_VALUE):
        if not key in self._prop_types:
            self._prop_types[key] = prop_type


    def set_template(self, key: str, template: str):
        if not key in self._templates:
            self._templates[key] = template


    def set(self, key: str, value: Any):
        if not key in self._keys:
            self._keys.append(key)
        if isinstance(value, (MultiItem, DynamicData)):
            setattr(self, key, value)
        elif isinstance(value, dict):
            setattr(self, key, self.type_hint(key)(value))
        elif isinstance(value, list):
            if len(value):
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
        else:
            setattr(self, key, value)


    def ensure(self, key: str, default: Any):
        if key in self._keys: return

        if hasattr(self, key) and getattr(self, key, None) != None:
            self._keys.append(key)
            return

        self.set(key, default)


    def as_dict(self, skip_none: bool = False) -> dict:
        result = {}

        for name in self._keys:
            v = getattr(self, name)
            if isinstance(v, MultiItem) and v.has_data:
                result[name] = v.as_dict()
            elif isinstance(v, DynamicData) and v.has_data:
                result[name] = v.as_dict(skip_none)
            elif isinstance(v, list):
                if isinstance(v[0], DynamicData):
                    result[name] = [ x.as_dict(skip_none) for x in v ]
                else:
                    if not skip_none or v is not None:
                        result[name] = v
            else:
                if not skip_none or v is not None:
                    result[name] = v
        
        return result


    def trim(self) -> DynamicData:
        pass


    @property
    def any(self) -> bool:
        return len(self._keys) > 0


    def is_value(self, key: str) -> bool:
        return self.is_prop_type(key, PROP_TYPE_VALUE)


    def is_template(self, key: str) -> bool:
        return self.is_prop_type(key, PROP_TYPE_TEMPLATE)


    def is_default(self, key: str) -> bool:
        return self.is_prop_type(key, PROP_TYPE_DEFAULT)


    def is_prop_type(self, key: str, prop_type: str) -> bool:
        return self._prop_types.get(key, None) == prop_type


    def get_template(self, key: str) -> str:
        return self._templates.get(key, None)


class MultiItem(DynamicData):

    def __init__(self, source: dict = None) -> None:
        super().__init__(source)


    class MultiItemIterator:
        
        def __init__(self, parent: Any, keys: list[str]):
            self.parent = parent
            self._keys = keys
            self.num = 0
            self.end = len(keys) - 1


        def __next__(self):
            if self.num > self.end:
                raise StopIteration
            else:
                result = getattr(self.parent, self._keys[self.num])
                self.num += 1
                return result


    def as_dict(self):
        return [getattr(self, name) for name in self._keys]


    def __iter__(self):
        return MultiItem.MultiItemIterator(self, self._keys)


    def __len__(self):
        return len(self._keys)


    def __contains__(self, key):
        for value in self:
            if value == key: 
                return True
        return False


    @property
    def first(self) -> Any:
        return self[0]


    @property
    def first_or_none(self) -> Any:
        if self.len() > 0:
            return self.first
        return None


    def __getitem__(self, k):
        if self.any and len(self._keys) > k:
            return self.get(self._keys[k])
        return None

    
    def len(self):
        return len(self._keys)


class CtorConfig(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.id: str = None
        self.index: int = None
        self.entity: Union[MultiItem, str] = None
        self.type: Union[MultiItem, str] = None
        self.action: Union[MultiItem, str] = None
        self.condition: str = None
        self.data: list[DynamicData] = None


class CtorRuntime(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.id: str = None
        self.index: int = None
        self.entity: MultiItem = None
        self.type: MultiItem = None
        self.action: MultiItem = None
        self.condition: bool = None
        self.data: list[DynamicData] = None
        
        self.ensure(ATTR_CONDITION, True)


class StateConfig(DynamicData):
    def __init__(self) -> None:
        super().__init__()

        self.condition: str = None
        self.restart_mode: str = RESTART_MODE_ABORT


class StateRuntime(DynamicData):
    def __init__(self) -> None:
        super().__init__()

        self.condition: bool = None
        self.restart_mode: str = RESTART_MODE_ABORT


class DelayData(DynamicData):
    def __init__(self) -> None:
        super().__init__()

        self.seconds: int = None
        self.minutes: int = None
        self.hours: int = None
        self.restart_mode: str = RESTART_MODE_ABORT


class ScheduleConfig(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.at: str = None
        self.weekdays: MultiItem = None
        self.restart_mode: str = RESTART_MODE_ABORT


class ScheduleRuntime(DynamicData):

    def __init__(self) -> None:
        super().__init__()

        self.at: datetime = None
        self.weekdays: MultiItem = None
        self.restart_mode: str = RESTART_MODE_ABORT


class WaitConfig(DynamicData):
    type_hints: dict = {
        ATTR_STATE: StateConfig,
        ATTR_DELAY: DelayData,
        ATTR_SCHEDULE: ScheduleConfig,
    }

    def __init__(self) -> None:
        super().__init__()

        self.state: StateConfig = None
        self.delay: DelayData = None
        self.schedule: ScheduleConfig = None
        

class WaitRuntime(DynamicData):

    type_hints: dict = {
        ATTR_STATE: StateRuntime,
        ATTR_DELAY: DelayData,
        ATTR_SCHEDULE: ScheduleRuntime,
    }

    def __init__(self) -> None:
        super().__init__()

        self.state: StateRuntime = None
        self.delay: DelayData = None
        self.schedule: ScheduleRuntime = None


class ActorConfig(CtorConfig):

    def __init__(self) -> None:
        super().__init__()


class ActorRuntime(CtorRuntime):

    def __init__(self) -> None:
        super().__init__()


class ReactorConfig(CtorConfig):

    def __init__(self) -> None:
        super().__init__()
        
        self.overwrite: Union[bool, str] = None
        self.reset_workflow: str = None
        self.forward_action: Union[bool, str] = None
        self.forward_data: Union[bool, str] = None
        self.wait: WaitConfig = None

        self.ensure(ATTR_OVERWRITE, False)
        self.ensure(ATTR_FORWARD_ACTION, False)
        self.ensure(ATTR_FORWARD_DATA, False)


class ReactorRuntime(CtorRuntime):

    type_hints: dict = {
        ATTR_WAIT: WaitRuntime,
    }

    def __init__(self) -> None:
        super().__init__()

        self.overwrite: bool = None
        self.reset_workflow: str = None
        self.forward_action: bool = None
        self.forward_data: bool = None
        self.wait: WaitRuntime = None

        self.ensure(ATTR_OVERWRITE, False)
        self.ensure(ATTR_FORWARD_ACTION, False)
        self.ensure(ATTR_FORWARD_DATA, False)
