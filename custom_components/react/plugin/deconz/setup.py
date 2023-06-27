import voluptuous as vol

from custom_components.react.const import CONF_ENTITY_MAPS

from custom_components.react.plugin.deconz.config import DeconzConfig
from custom_components.react.plugin.deconz.input.double_press_input_block import DeconzDoublePressInputBlock
from custom_components.react.plugin.deconz.input.long_press_input_block import DeconzLongPressInputBlock
from custom_components.react.plugin.deconz.input.short_press_input_block import DeconzShortPressInputBlock
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup

TELEGRAM_PLUGIN_SCHEMA = vol.Schema({
    CONF_ENTITY_MAPS: dict
})


class Setup(PluginSetup[DeconzConfig]):
    def __init__(self) -> None:
        super().__init__(TELEGRAM_PLUGIN_SCHEMA)


    def setup_config(self, raw_config: dict) -> DeconzConfig:
        return DeconzConfig(raw_config)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup([
            DeconzShortPressInputBlock,
            DeconzLongPressInputBlock,
            DeconzDoublePressInputBlock,
        ])
