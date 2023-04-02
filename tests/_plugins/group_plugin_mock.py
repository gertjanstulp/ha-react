from typing import Any

from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.components.group.notify import GroupNotifyPlatform
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.notify.legacy import NOTIFY_SERVICES, BaseNotificationService
from homeassistant.const import ATTR_SERVICE
from homeassistant.core import HomeAssistant
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY

from custom_components.react.plugin.notify.plugin import load as load_notify_plugin
from custom_components.react.plugin.group.plugin import load as load_group_plugin
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests._plugins.notify_plugin_mock import NOTIFY_PROVIDER_MOCK, setup_mock_notify_provider
from tests.const import (
    ATTR_NOTIFY_PROVIDER, 
    ATTR_SERVICE_NAME
)

ATTR_CHILD_SERVICE = "child_service"
ATTR_KILL_RESOLVER = "kill_resolver"
ATTR_KILL_CHILD_PROVIDER = "kill_child_provider"

def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_group_plugin(plugin_api, hass_api_mock, config)

    if notify_provider:= config.get(ATTR_NOTIFY_PROVIDER):
        load_notify_plugin(
            plugin_api, 
            hass_api_mock, 
            { 
                ATTR_NOTIFY_PROVIDER: notify_provider,
            }
        )
        if not config.get(ATTR_KILL_CHILD_PROVIDER, False):
            setup_mock_notify_provider(plugin_api, hass_api, NOTIFY_PROVIDER_MOCK)
    
    if notify_service := config.get(ATTR_SERVICE_NAME):
        hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)

        if child_service := config.get(ATTR_CHILD_SERVICE, None):
            notify_services: dict[str, list[GroupNotifyPlatform]] = {}
            notify_services[GROUP_DOMAIN] = [
                MockGroupNotifyPlatform(hass_api.hass, notify_service, [{ATTR_SERVICE: child_service}])
            ]
            notify_services[NOTIFY_PROVIDER_MOCK] = [
                MockNotifyPlatform(child_service)
            ]

            hass_api_mock.hass_set_data(NOTIFY_SERVICES, notify_services)
            hass_api_mock.hass_register_service(NOTIFY_DOMAIN, child_service)

    if config.get(ATTR_KILL_RESOLVER, False):
        hass_api.hass_set_data(NOTIFY_RESOLVER_KEY, None)


class MockGroupNotifyPlatform(GroupNotifyPlatform):
    def __init__(self, hass: HomeAssistant, service_name: str, entities: list[dict[str, Any]]) -> None:
        super().__init__(hass, entities)
        self._service_name = service_name


class MockNotifyPlatform(BaseNotificationService):
    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name
