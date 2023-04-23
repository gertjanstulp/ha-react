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
from tests.const import ATTR_ENTITY_STATE
from tests.tst_context import TstContext


def get_mock_plugin(
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.google_translate_plugin_mock", 
        ATTR_CONFIG: {}
    }
    if media_player_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_CONFIG][ATTR_ENTITY_STATE] = media_player_entity_state
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_test"])
async def test_google_translate_plugin_provider_speek(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_CONTENT_ID: f"This is a test without volume|{TTS_GOOGLE_TRANSLATE_PROVIDER}|{TTS_DEFAULT_LANGUAGE}",
        ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        ATTR_MEDIA_ANNOUNCE: True,
    }
    
    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_PLAY_MEDIA, data)
