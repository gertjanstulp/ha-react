import pytest

from homeassistant.components.media_player import (
    ATTR_MEDIA_VOLUME_LEVEL,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_VOLUME_SET,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG

from tests._plugins.media_player_plugin_mock import TTS_PROVIDER_MOCK
from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_TTS_PROVIDER
)
from tests.tst_context import TstContext


def get_mock_plugin(
    tts_provider: str = None,
    media_player_entity_id: str = None,
    media_player_entity_state: str = None
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.browser_mod_plugin_mock", 
        ATTR_CONFIG: {}
    }
    if tts_provider:
        result[ATTR_CONFIG][ATTR_TTS_PROVIDER] = tts_provider
    if media_player_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = media_player_entity_id
    if media_player_entity_state != None:
        result[ATTR_CONFIG][ATTR_ENTITY_STATE] = media_player_entity_state
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_speek_with_volume_test"])
async def test_browser_mod_plugin_provider_speek_with_volume(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "media_player.browser"
    mock_plugin = get_mock_plugin(
        tts_provider=TTS_PROVIDER_MOCK,
        media_player_entity_id=entity_id,
        media_player_entity_state="stopped",
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data_volume = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_MEDIA_VOLUME_LEVEL: 0.1
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
        tc.verify_service_call_content(MEDIA_PLAYER_DOMAIN, SERVICE_VOLUME_SET, plugin_data_volume)
