from custom_components.react.utils.struct import DynamicData


class GoogleTranslateConfig(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.language: str = None
        self.options: DynamicData = None
        self.load(source)
