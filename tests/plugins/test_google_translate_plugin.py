import pytest

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    MediaType,
    SERVICE_PLAY_MEDIA
)
from homeassistant.components.tts import (
    ATTR_OPTIONS,
    ATTR_LANGUAGE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_PLUGIN_MODULE, DOMAIN
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.google_translate.const import TTS_GOOGLE_TRANSLATE_PROVIDER
from custom_components.react.plugin.media_player.const import TTS_DEFAULT_LANGUAGE

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.const import ATTR_ENTITY_STATE, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if media_player_entity_id:
        result[ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_ENTITY_STATE] = media_player_entity_state


def get_mock_plugin(
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.google_translate_mock", 
        ATTR_CONFIG: {}
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek(test_context: TstContext, workflow_name: str):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    await test_context.async_start_react(mock_plugin)
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{TTS_DEFAULT_LANGUAGE}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data)
