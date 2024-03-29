from custom_components.react.utils.struct import DynamicData


class SwitchConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.switch_provider: str = None
        self.load(source)