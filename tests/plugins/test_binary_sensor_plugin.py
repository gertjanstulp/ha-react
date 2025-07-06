import pytest

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_ON
from custom_components.react.const import (
    ACTION_AVAILABLE,
    ACTION_CHANGE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_PLUGIN_MODULE,
)
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
        ATTR_PLUGIN_MODULE: "tests._plugins.binary_sensor_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_state_test"])
async def test_binary_sensor_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "binary_sensor_state_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        test_context.verify_reaction_not_found()
        await vc.async_turn_on(BINARY_SENSOR_DOMAIN, entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=STATE_ON,
            event_with_action_name=STATE_ON)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_with_action_name=ACTION_TOGGLE)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_available_test"])
async def test_binary_sensor_available(test_context: TstContext, workflow_name: str):
    entity_id = "binary_sensor_available_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        await vc.async_set_available(BINARY_SENSOR_DOMAIN, entity_id)
        await test_context.async_verify_action_event_received(expected_count=2)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_AVAILABLE,
            event_with_action_name=ACTION_AVAILABLE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_unavailable_test"])
async def test_binary_sensor_unavailable(test_context: TstContext, workflow_name: str):
    entity_id = "binary_sensor_unavailable_test"
    mock_plugin = get_mock_plugin()
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await vc.async_set_unavailable(BINARY_SENSOR_DOMAIN, entity_id)
        await test_context.async_verify_action_event_received(expected_count=2)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_UNAVAILABLE,
            event_with_action_name=ACTION_UNAVAILABLE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BINARY_SENSOR_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_has_no_log_issues()