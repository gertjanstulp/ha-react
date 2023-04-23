from custom_components.react.utils.struct import DynamicData


class NotifyConfig(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.notify_provider_name: str = None
        self.load(source)