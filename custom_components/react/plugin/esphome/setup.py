import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.esphome.const import (
    ATTR_ENTITY_PROPERTY,
    ATTR_TYPE_MAPS, 
)
from custom_components.react.plugin.esphome.input.event_input_block import EspHomeEventInputBlock
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.esphome.config import EspHomeActionMap, EspHomeConfig

ESPHOME_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_PROPERTY) : cv.string,
    vol.Required(ATTR_TYPE_MAPS) : vol.Schema({
        cv.slug: vol.Schema({
            cv.slug: cv.string
        })
    })
})


class Setup(PluginSetup[EspHomeConfig]):
    def __init__(self) -> None:
        super().__init__(ESPHOME_PLUGIN_CONFIG_SCHEMA)

    
    def setup_config(self, raw_config: dict) -> EspHomeConfig:
        return EspHomeConfig(raw_config)
    

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        for react_type in self.plugin.config.type_maps.keys():
            action_map: EspHomeActionMap = self.plugin.config.type_maps.get(react_type)
            for esphome_event_name in action_map.keys():
                setup(
                    EspHomeEventInputBlock, 
                    entity_property=self.plugin.config.entity_property,
                    react_type=react_type,
                    esphome_event_name=esphome_event_name,
                    react_action=action_map.get(esphome_event_name)
                )
