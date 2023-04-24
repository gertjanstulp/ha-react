from homeassistant.components.telegram import DOMAIN as TELEGRAM_DOMAIN
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER

from custom_components.react.plugin.notify.plugin import Plugin as NotifyPlugin
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.telegram.plugin import Plugin as  TelegramPlugin
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.const import ATTR_SERVICE_NAME, TEST_CONFIG


class Plugin(TelegramPlugin):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        hass_api_mock = HassApiMock(hass_api.hass)
        super().load(plugin_api, hass_api_mock, config)

        NotifyPlugin().load(
            plugin_api, 
            hass_api_mock, 
            { 
                ATTR_NOTIFY_PROVIDER: TELEGRAM_DOMAIN,
            }
        )
        
        test_config: dict = hass_api.hass_get_data(TEST_CONFIG, {})
        notify_service = test_config.get(ATTR_SERVICE_NAME)
        if notify_service:
            hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)
