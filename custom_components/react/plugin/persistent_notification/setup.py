from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.persistent_notification.const import NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION
from custom_components.react.plugin.persistent_notification.provider import PersistentNotificationProvider
from custom_components.react.plugin.persistent_notification.input.notification_dismissed_input_block import NotificationDismissedInputBlock
from custom_components.react.utils.struct import DynamicData


class Setup(PluginSetup[DynamicData]):
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(PersistentNotificationProvider, PROVIDER_TYPE_NOTIFY, NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(NotificationDismissedInputBlock)
