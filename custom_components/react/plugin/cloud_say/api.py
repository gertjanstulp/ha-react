from homeassistant.const import Platform
from homeassistant.core import Context

from custom_components.react.base import ReactBase


class Api():
    def __init__(self, react: ReactBase) -> None:
        self.react = react