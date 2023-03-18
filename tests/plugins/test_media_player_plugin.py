from unittest.mock import Mock
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_PLUGIN_MODULE, DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.tst_context import TstContext

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_media"])
async def test_media_player_play_media(hass: HomeAssistant, workflow_name, react_component: Mock):
    
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.media_player_plugin_play_media_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "media_player_play_media_test",
        ATTR_MEDIA_CONTENT_TYPE: "test_type",
        ATTR_MEDIA_CONTENT_ID: "test_id"
        
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(plugin_data)