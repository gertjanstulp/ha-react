from homeassistant.components.tts import ATTR_OPTIONS

from custom_components.react.utils.struct import DynamicData


class CloudConfigOptions(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.voice: str = None
        self.load(source)


class CloudConfig(DynamicData):
    type_hints: dict = {
        ATTR_OPTIONS: CloudConfigOptions,
    }

    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.type_hints 
        self.language: str = None
        self.options: CloudConfigOptions = None
        self.load(source)
