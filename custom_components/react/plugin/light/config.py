from custom_components.react.utils.struct import DynamicData


class LightConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.light_provider: str = None
        self.load(source)