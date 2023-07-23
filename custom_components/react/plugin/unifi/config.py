from custom_components.react.utils.struct import DynamicData


class UnifiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.unifi_provider: str = None
        self.load(source)
