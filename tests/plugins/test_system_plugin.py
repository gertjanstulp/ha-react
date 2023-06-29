import pytest

from custom_components.react.const import (
    ACTION_SHUTDOWN, 
    ACTION_START, 
    ACTION_STARTED, 
    ATTR_PLUGIN_MODULE, 
    ENTITY_HASS, 
    TYPE_SYSTEM,
)
from custom_components.react.plugin.const import ATTR_CONFIG

from tests._plugins.system_mock.setup import (
    SKIP_START_INPUT_BLOCK, 
    SKIP_STARTED_INPUT_BLOCK,
)
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    skip_start_task: bool = False,
    skip_started_task: bool = False,
) -> dict:
    test_context.hass.data[TEST_CONFIG] = {
        SKIP_START_INPUT_BLOCK : skip_start_task,
        SKIP_STARTED_INPUT_BLOCK : skip_started_task,
    }


def get_mock_plugin(
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.system_mock",
        ATTR_CONFIG: {} 
    }
    return result





@pytest.mark.enable_socket
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["system_hass_start_test"])
async def test_system_plugin_hass_start_action(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        skip_started_task=True
    )
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await test_context.hass.async_start()
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=ENTITY_HASS,
            expected_type=TYPE_SYSTEM,
            expected_action=ACTION_START,
            event_index=0)
        test_context.verify_has_no_log_issues()


@pytest.mark.enable_socket
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["system_hass_started_test"])
async def test_system_plugin_hass_started_action(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        skip_start_task=True
    )
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await test_context.hass.async_start()
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=ENTITY_HASS,
            expected_type=TYPE_SYSTEM,
            expected_action=ACTION_STARTED,
            event_index=0)
        test_context.verify_has_no_log_issues()


@pytest.mark.enable_socket
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["system_hass_shutdown_test"])
async def test_system_plugin_hass_shutdown_action(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        skip_start_task=True,
        skip_started_task=True,
    )
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await test_context.hass.async_start()
        await test_context.hass.async_block_till_done()
        await test_context.hass.async_stop()
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=1)
        test_context.verify_action_event_data(
            expected_entity=ENTITY_HASS,
            expected_type=TYPE_SYSTEM,
            expected_action=ACTION_SHUTDOWN,
            event_index=0)
        test_context.verify_has_no_log_issues()