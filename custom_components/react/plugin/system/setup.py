from custom_components.react.plugin.const import PROVIDER_TYPE_SYSTEM
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.system.api import SystemApi
from custom_components.react.plugin.system.config import SystemConfig
from custom_components.react.plugin.system.const import SYSTEM_GENERIC_PROVIDER
from custom_components.react.plugin.system.input.hass_shutdown_input_block import SystemHassEventShutdownInputBlock
from custom_components.react.plugin.system.input.hass_start_input_block import SystemHassEventStartInputBlock
from custom_components.react.plugin.system.input.hass_started_input_block import SystemHassEventStartedInputBlock
from custom_components.react.plugin.system.output.hass_shutdown_output_block import SystemHassShutdownOutputBlock
from custom_components.react.plugin.system.provider import SystemProvider


class Setup(PluginSetup):

    def setup_config(self, raw_config: dict):
        return SystemConfig(raw_config)
    
    
    def setup_api(self, setup: ApiSetupCallback):
        setup(SystemApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(SystemProvider, PROVIDER_TYPE_SYSTEM, SYSTEM_GENERIC_PROVIDER)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup([
            SystemHassEventStartInputBlock,
            SystemHassEventStartedInputBlock,
            SystemHassEventShutdownInputBlock,
        ])
    

    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup([
            SystemHassShutdownOutputBlock
        ])
