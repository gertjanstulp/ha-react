from homeassistant.components.telegram import DOMAIN as TELEGRAM_DOMAIN
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN

from custom_components.react.plugin.notify.plugin import load as load_notify_plugin
from custom_components.react.plugin.telegram.plugin import load as load_telegram_plugin
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.const import ATTR_NOTIFY_PROVIDER, ATTR_SERVICE_NAME


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_telegram_plugin(plugin_api, hass_api_mock, config)

    load_notify_plugin(
        plugin_api, 
        hass_api_mock, 
        { 
            ATTR_NOTIFY_PROVIDER: TELEGRAM_DOMAIN,
        }
    )
    
    notify_service = config.get(ATTR_SERVICE_NAME)
    if notify_service:
        hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)
