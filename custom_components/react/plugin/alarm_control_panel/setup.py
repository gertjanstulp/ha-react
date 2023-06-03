import voluptuous as vol

from homeassistant.const import ATTR_CODE
from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.alarm_control_panel.api import AlarmApi
from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig
from custom_components.react.plugin.alarm_control_panel.const import ALARM_GENERIC_PROVIDER, ATTR_ALARM_PROVIDER
from custom_components.react.plugin.alarm_control_panel.provider import AlarmProvider
from custom_components.react.plugin.alarm_control_panel.output.arm_away_output_block import AlarmArmAwayOutputBlock
from custom_components.react.plugin.alarm_control_panel.output.arm_home_output_block import AlarmArmHomeOutputBlock
from custom_components.react.plugin.alarm_control_panel.output.arm_night_output_block import AlarmArmNightOutputBlock
from custom_components.react.plugin.alarm_control_panel.output.arm_vacation_output_block import AlarmArmVacationOutputBlock
from custom_components.react.plugin.alarm_control_panel.output.disarm_output_block import AlarmDisarmOutputBlock
from custom_components.react.plugin.alarm_control_panel.input.state_change_input_block import AlarmStateChangeInputBlock
from custom_components.react.plugin.alarm_control_panel.output.trigger_output_block import AlarmTriggerOutputBlock
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM_CONTROL_PANEL
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback

ALARM_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Required(ATTR_CODE) : cv.string,
    vol.Optional(ATTR_ALARM_PROVIDER) : cv.string,
})
    

class Setup(PluginSetup[AlarmConfig]):
    def __init__(self) -> None:
        super().__init__(ALARM_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> AlarmConfig:
        return AlarmConfig(raw_config)


    def setup_api(self, setup: ApiSetupCallback):
        setup(AlarmApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(AlarmProvider, PROVIDER_TYPE_ALARM_CONTROL_PANEL, ALARM_GENERIC_PROVIDER)
        

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(AlarmStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                AlarmArmHomeOutputBlock,
                AlarmArmAwayOutputBlock,
                AlarmArmNightOutputBlock,
                AlarmArmVacationOutputBlock,
                AlarmDisarmOutputBlock,
                AlarmTriggerOutputBlock,
            ],
        )
