import pytest

from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER_DOMAIN
from homeassistant.const import STATE_HOME

from custom_components.react.const import ACTION_CHANGE, ACTION_TOGGLE, ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
) -> dict:
    test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.device_tracker_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker_state_test"])
async def test_device_tracker_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "device_tracker_state_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_virtual()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        test_context.verify_reaction_not_found()
        await dtc.async_see(entity_id, STATE_HOME)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=DEVICE_TRACKER_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=DEVICE_TRACKER_DOMAIN,
            expected_action=f"{STATE_HOME}",
            event_index=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=DEVICE_TRACKER_DOMAIN,
            expected_action=f"{ACTION_TOGGLE}",
            event_index=2)
        test_context.verify_has_no_log_issues()

    await test_context.hass.async_block_till_done()
    

# @pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker_available_test"])
# async def test_device_tracker_available(test_context: TstContext, workflow_name: str):
#     entity_id = "device_tracker_available_test"
#     mock_plugin = get_mock_plugin()
#     await test_context.async_start_device_tracker()
#     await test_context.hass.async_block_till_done()
#     vc = await test_context.async_start_virtual()
#     await test_context.async_start_react([mock_plugin])

#     async with test_context.async_listen_reaction_event():
#         test_context.verify_reaction_not_found()
#         await vc.async_set_available(DEVICE_TRACKER_DOMAIN, entity_id)
#         test_context.verify_reaction_not_found()
#         await test_context.async_verify_reaction_event_received()
#         test_context.verify_reaction_event_data()
#         test_context.verify_trace_record()