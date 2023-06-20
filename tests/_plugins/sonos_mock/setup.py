from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.plugin.sonos.setup import Setup as SonosSetup

from tests._plugins.common import HassApiMockExtend
from tests.const import (
    ATTR_ENTITY_STATE,
    TEST_CONFIG, 
)


class Setup(SonosSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        media_player_entity_id = test_config.get(ATTR_ENTITY_ID)
        media_player_state = test_config.get(ATTR_ENTITY_STATE, None)
        if media_player_entity_id and media_player_state != None:
            self.hass_api_mock.hass_register_state(media_player_entity_id, media_player_state)
