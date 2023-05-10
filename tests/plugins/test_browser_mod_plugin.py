import pytest

from homeassistant.components.media_player import (
    ATTR_MEDIA_VOLUME_LEVEL,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_VOLUME_SET,
)
from homeassistant.components.tts import ATTR_LANGUAGE
from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.browser_mod.const import MEDIA_PLAYER_BROWSER_MOD_PROVIDER
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.media_player.const import ATTR_MEDIA_PLAYER_PROVIDER, ATTR_TTS_PROVIDER
from tests._plugins.media_player_mock.const import ATTR_SETUP_MOCK_TTS_PROVIDER

from tests._plugins.media_player_mock.setup import TTS_PROVIDER_MOCK
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_MESSAGE,
    ATTR_VOLUME,
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_tts_provider: bool = False,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_TTS_PROVIDER: setup_mock_tts_provider
    }
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state


def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.browser_mod_mock", 
            ATTR_CONFIG: {}
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.media_player_mock", 
            ATTR_CONFIG: { 
                ATTR_MEDIA_PLAYER_PROVIDER: MEDIA_PLAYER_BROWSER_MOD_PROVIDER,
                ATTR_TTS_PROVIDER: TTS_PROVIDER_MOCK,
            }
        },
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_browser_mod_plugin_provider_speek_with_volume(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_tts_provider=True,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugins)
    
    data_in = {
        ATTR_MESSAGE: "This is a test with volume",
        ATTR_LANGUAGE: "en",
        ATTR_VOLUME: 0.1,
    }

    plugin_data_volume = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_VOLUME_SET, plugin_data_volume)
