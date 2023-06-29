from custom_components.react.const import REACT_TYPE_BUTTON
from custom_components.react.plugin.esphome.const import ATTR_TYPE_MAPS
from custom_components.react.utils.struct import DynamicData


class EspHomeActionMap(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.load(source)


class EspHomeTypeMap(DynamicData):
    type_hints: dict = {
        REACT_TYPE_BUTTON: EspHomeActionMap,
    }

    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.button: EspHomeActionMap
        self.load(source)


class EspHomeConfig(DynamicData):
    type_hints: dict = {
        ATTR_TYPE_MAPS: EspHomeTypeMap,
    }
    
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.entity_property: str = None
        self.type_maps: EspHomeTypeMap = None
        self.load(source)