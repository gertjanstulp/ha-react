from custom_components.react.utils.struct import DynamicData


class InputConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.input_provider_name: str = None
        self.load(source)
