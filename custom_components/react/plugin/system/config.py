from custom_components.react.utils.struct import DynamicData


class SystemConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.system_provider: str = None
        self.load(source)