from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN

from custom_components.react.plugin.persistent_notification.setup import Setup as PersistentNotificationSetup

from tests._plugins.common import HassApiMockExtend
from tests.const import (
    ATTR_SERVICE_NAME, 
    TEST_CONFIG
)


class Setup(PersistentNotificationSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        notify_service = test_config.get(ATTR_SERVICE_NAME)
        if notify_service:
            self.hass_api_mock.hass_register_service(NOTIFY_DOMAIN, notify_service)
