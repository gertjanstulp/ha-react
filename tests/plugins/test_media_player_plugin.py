import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_PLUGIN_MODULE, DOMAIN
from custom_components.react.plugin.const import ATTR_CONFIG, ATTR_DEFAULT_SERVICE_TYPE
from custom_components.react.plugin.media_player.const import ATTR_FAVORITE_ID
from custom_components.react.utils.logger import get_react_logger
from tests._mocks.mock_log_handler import MockLogHandler

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_play_favorite_no_service(hass: HomeAssistant, workflow_name, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.media_player_plugin_mock", ATTR_CONFIG : {ATTR_DEFAULT_SERVICE_TYPE: "dummy"}}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_not_sent()
        tc.verify_has_log_record("ERROR", "Mediaplayer plugin: Api - Service for 'dummy' not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["media_player_play_favorite_test"])
async def test_media_player_play_favorite(hass: HomeAssistant, workflow_name, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.media_player_plugin_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "media_player_play_favorite_test",
        ATTR_FAVORITE_ID: "test_id"
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