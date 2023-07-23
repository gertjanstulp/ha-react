from custom_components.react.utils.struct import DynamicData


class HassioConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.hassio_provider: str = None
        self.load(source)
