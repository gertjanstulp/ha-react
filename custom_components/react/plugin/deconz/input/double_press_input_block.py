from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_DOUBLE_PRESS
from custom_components.react.plugin.deconz.const import DECONZ_CODE_DOUBLE_PRESS
from custom_components.react.plugin.deconz.input.button_input_block import DeconzButtonInputBlock


class DeconzDoublePressInputBlock(DeconzButtonInputBlock):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DECONZ_CODE_DOUBLE_PRESS, REACT_ACTION_DOUBLE_PRESS, "double press")
    