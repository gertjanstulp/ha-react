from custom_components.react.utils.struct import DynamicData


class InputBooleanConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.input_boolean_provider: str = None
        self.load(source)
