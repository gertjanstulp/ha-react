
from typing import Any


class DynamicData():
    def __init__(self, source: dict) -> None:
        self.names: list[str] = []
        if not source: return

        type_hints: dict = {}
        if hasattr(self, "type_hints"):
            type_hints = getattr(self, "type_hints")

        def type_hint(key):
            return type_hints.get(key, DynamicData)

        for k,v in source.items():
            self.names.append(k)
            if isinstance(v, dict):
                setattr(self, k, type_hint(k)(v))
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], dict):
                    items = []
                    for item in v:
                        items.append(type_hint(k)(item))
                    setattr(self, k, items)
                else:
                    # items.append(type_hint(k)({"_value_" : item}))
                    setattr(self, k, MultiItem( {f"_{index}":item for index,item in enumerate(v)} ))
            else:
                setattr(self, k, v)


    def as_dict(self) -> dict:
        result = {}

        for name in self.names:
            v = getattr(self, name)
            if isinstance(v, DynamicData):
                result[name] = v.as_dict()
            elif isinstance(v, list):
                if isinstance(v[0], DynamicData):
                    result[name] = [ x.as_dict() for x in v ]
                else:
                    result[name] = v
            else:
                result[name] = v
        
        return result


class MultiItem(DynamicData):
    def __init__(self, source: dict) -> None:
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