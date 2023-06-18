from custom_components.react.utils.struct import DynamicData


class ClimateConfig(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.climate_provider: str = None
        self.load(source)
