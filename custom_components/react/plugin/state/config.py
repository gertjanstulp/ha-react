from __future__ import annotations

from custom_components.react.utils.struct import DynamicData


class StateConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.state_provider: str = None
        self.load(source)
