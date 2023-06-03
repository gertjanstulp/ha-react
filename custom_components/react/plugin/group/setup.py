from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP
from custom_components.react.plugin.group.provider import GroupProvider
from custom_components.react.plugin.group.input.state_change_input_block import GroupStateChangeInputBlock


class Setup(PluginSetup):
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(GroupProvider, PROVIDER_TYPE_NOTIFY, NOTIFY_PROVIDER_GROUP)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(GroupStateChangeInputBlock)
