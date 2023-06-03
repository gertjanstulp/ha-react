from custom_components.react.utils.struct import DynamicData


class InputTextConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.input_text_provider: str = None
        self.load(source)
