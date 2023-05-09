from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.persistent_notification import DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN

from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER
from custom_components.react.plugin.notify.plugin import Plugin as NotifyPlugin
from custom_components.react.plugin.persistent_notification.plugin import Plugin as PersistentNotificationPlugin
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.const import (
    ATTR_SERVICE_NAME, 
    TEST_CONFIG
)


class Plugin(PersistentNotificationPlugin):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        hass_api_mock = HassApiMock(hass_api.hass)
        super().load(plugin_api, hass_api_mock, config)

        NotifyPlugin().load(
            plugin_api, 
            hass_api_mock, 
            { 
                ATTR_NOTIFY_PROVIDER: PERSISTENT_NOTIFICATION_DOMAIN,
            }
        )
        
        test_config: dict = hass_api.hass_get_data(TEST_CONFIG, {})
        notify_service = test_config.get(ATTR_SERVICE_NAME)
        if notify_service:
            hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)
