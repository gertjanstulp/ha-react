from custom_components.react.utils.struct import DynamicData


class DeconzConfig(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.entity_maps: DynamicData = None
        self.load(source)