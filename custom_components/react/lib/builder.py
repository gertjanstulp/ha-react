
from typing import Any
from .config import Actor


class Builder:
    def __init__(self) -> None:
        pass


    def build(self, actor: Actor):
        result = type('object', (), {})()
        result_wrapper = ObjectWrapper(result)


    def build_recursive(self, item: Any):
        
        pass
        

class ObjectWrapper:
    object: object = None

    def __init__(self, object: object) -> None:
        self.object = object

