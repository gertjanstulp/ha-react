from typing import Any

from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.components.group.notify import GroupNotifyPlatform
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.components.notify.legacy import NOTIFY_SERVICES, BaseNotificationService
from homeassistant.const import ATTR_SERVICE
from homeassistant.core import HomeAssistant

from custom_components.react.plugin.group.setup import Setup as GroupSetup
from custom_components.react.plugin.notify.const import NOTIFY_RESOLVER_KEY

from tests._plugins.common import HassApiMockExtend
from tests._plugins.notify_mock.setup import NOTIFY_PROVIDER_MOCK
from tests.const import (
    ATTR_SERVICE_NAME,
    TEST_CONFIG
)

ATTR_CHILD_SERVICE = "child_service"
ATTR_KILL_RESOLVER = "kill_resolver"
ATTR_KILL_CHILD_PROVIDER = "kill_child_provider"


class Setup(GroupSetup, HassApiMockExtend):
    

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.kill_child_provider = test_config.get(ATTR_KILL_CHILD_PROVIDER, False)

        if notify_service := test_config.get(ATTR_SERVICE_NAME):
            self.hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)

            if child_service := test_config.get(ATTR_CHILD_SERVICE, None):
                notify_services: dict[str, list[GroupNotifyPlatform]] = {}
                notify_services[GROUP_DOMAIN] = [
                    MockGroupNotifyPlatform(self.hass_api_mock.hass, notify_service, [{ATTR_SERVICE: child_service}])
                ]
                notify_services[NOTIFY_PROVIDER_MOCK] = [
                    MockNotifyPlatform(child_service)
                ]

                self.hass_api_mock.hass_set_data(NOTIFY_SERVICES, notify_services)
                self.hass_api_mock.hass_register_service(NOTIFY_DOMAIN, child_service)

        if test_config.get(ATTR_KILL_RESOLVER, False):
            self.hass_api_mock.hass_set_data(NOTIFY_RESOLVER_KEY, None)


class MockGroupNotifyPlatform(GroupNotifyPlatform):
    def __init__(self, hass: HomeAssistant, service_name: str, entities: list[dict[str, Any]]) -> None:
        super().__init__(hass, entities)
        self._service_name = service_name


class MockNotifyPlatform(BaseNotificationService):
    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name
