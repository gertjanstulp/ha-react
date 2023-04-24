from __future__ import annotations

from custom_components.react.plugin.google_translate.const import ATTR_TTS_TLD
from custom_components.react.utils.struct import DynamicData


class GoogleTranslateConfigOptions(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.tld: str = None
        self.load(source)


class GoogleTranslateConfig(DynamicData):
    type_hints: dict = {
        ATTR_TTS_TLD: GoogleTranslateConfigOptions,
    }

    def __init__(self, source: dict = None) -> None:
        super().__init__()
        self.type_hints 
        self.language: str = None
        self.options: GoogleTranslateConfigOptions = None
        self.load(source)
