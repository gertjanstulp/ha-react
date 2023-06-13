from custom_components.react.utils.struct import DynamicData


class FanConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.fan_provider: str = None
        self.on_percentage: int = None
        self.off_percentage: int = None
        self.load(source)