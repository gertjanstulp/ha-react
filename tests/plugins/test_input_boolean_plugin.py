from typing import Any
import pytest

from homeassistant.components.input_boolean import (
    DOMAIN as BOOLEAN_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ACTION_TOGGLE,
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.input_boolean.const import ATTR_INPUT_BOOLEAN_PROVIDER
from tests._plugins.input_boolean_mock.setup import INPUT_BOOLEAN_MOCK_PROVIDER

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import ATTR_ENTITY_STATE, ATTR_SETUP_MOCK_PROVIDER, TEST_CONFIG
from tests.tst_context import TstContext

FIXTURE_INPUT_BOOLEAN_NAME = "input_boolean_name"
FIXTURE_VALUE_BEFORE = "value_before"
FIXTURE_VALUE_AFTER = "value_after"
FIXTURE_NAME_INITIAL = "name_initial"
FIXTURE_EXPECTED_SERVICE = "expected_service"
FIXTURE_INITIAL_STATE = "initial_state"
FIXTURE_ENTITY_ID = "entity_id"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    input_boolean_entity_id: str = None,
    input_boolean_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if input_boolean_entity_id:
        result[ATTR_ENTITY_ID] = input_boolean_entity_id
    if input_boolean_entity_state != None:
        result[ATTR_ENTITY_STATE] = input_boolean_entity_state


def get_mock_plugin(
    input_boolean_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_boolean_mock",
        ATTR_CONFIG: {} 
    }
    if input_boolean_provider:
        result[ATTR_CONFIG][ATTR_INPUT_BOOLEAN_PROVIDER] = input_boolean_provider
    return result


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_INPUT_BOOLEAN_NAME}", [
    ("input_boolean_turn_on_test", "initial_off"),
    ("input_boolean_turn_off_test", "initial_on"),
    ("input_boolean_toggle_test", "initial_off"),
])
async def test_input_boolean_plugin_api_set_invalid_entity(test_context: TstContext, workflow_name: str, input_boolean_name: str):
    mock_plugin = get_mock_plugin(
        input_boolean_provider=INPUT_BOOLEAN_MOCK_PROVIDER,
    )
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - input_boolean.input_boolean_{input_boolean_name}_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "input_boolean_turn_on_test",
    "input_boolean_turn_off_test",
    "input_boolean_toggle_test",
])
async def test_input_boolean_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "input_boolean.input_boolean_initial_off_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_boolean_entity_id=entity_id,
        input_boolean_entity_state="Off"
    )
    
    data = {
        ATTR_INPUT_BOOLEAN_PROVIDER: invalid_provider
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Input_boolean provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_NAME_INITIAL}", [
    ("input_boolean_turn_on_test",STATE_OFF,STATE_ON,STATE_OFF),
    ("input_boolean_turn_off_test",STATE_ON,STATE_OFF,STATE_ON),
    ("input_boolean_toggle_test",STATE_OFF,STATE_ON,STATE_OFF),
    ("input_boolean_toggle_test",STATE_ON,STATE_OFF,STATE_OFF),
])
async def test_input_boolean_plugin_api_set_config_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):
    entity_id = f"input_boolean.input_boolean_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        input_boolean_provider=INPUT_BOOLEAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        input_boolean_entity_id=entity_id,
        input_boolean_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data)


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_NAME_INITIAL}", [
    ("input_boolean_turn_on_test",STATE_OFF,STATE_ON,STATE_OFF),
    ("input_boolean_turn_off_test",STATE_ON,STATE_OFF,STATE_ON),
    ("input_boolean_toggle_test",STATE_OFF,STATE_ON,STATE_OFF),
    ("input_boolean_toggle_test",STATE_ON,STATE_OFF,STATE_OFF),
])
async def test_input_boolean_plugin_api_set_event_provider(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):
    entity_id = f"input_boolean.input_boolean_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        input_boolean_entity_id=entity_id,
        input_boolean_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data_in = {
        ATTR_INPUT_BOOLEAN_PROVIDER: INPUT_BOOLEAN_MOCK_PROVIDER
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_state_test"])
async def test_input_boolean_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "input_boolean_state_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    ibc = await test_context.async_start_input_boolean()
    await test_context.async_start_react([mock_plugin])

    async with test_context.async_listen_action_event():
        await ibc.async_turn_on(entity_id)
        await test_context.hass.async_block_till_done()
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BOOLEAN_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_index=0)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BOOLEAN_DOMAIN,
            expected_action=STATE_ON,
            event_index=1)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=BOOLEAN_DOMAIN,
            expected_action=ACTION_TOGGLE,
            event_index=2)
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_VALUE_BEFORE},{FIXTURE_VALUE_AFTER},{FIXTURE_EXPECTED_SERVICE}", [
    ("input_boolean_turn_on_test",STATE_OFF,STATE_ON,SERVICE_TURN_ON),
    ("input_boolean_turn_off_test",STATE_ON,STATE_OFF,SERVICE_TURN_OFF),
])
async def test_input_boolean_plugin_generic_provider_set(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, expected_service: str):
    entity_id = f"input_boolean.input_boolean_initial_{value_before}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_boolean_entity_id=entity_id,
        input_boolean_entity_state=value_before
    )

    await test_context.async_start_react([mock_plugin])
        
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(BOOLEAN_DOMAIN, expected_service, data)
    

@pytest.mark.parametrize(F"{FIXTURE_WORKFLOW_NAME},{FIXTURE_INITIAL_STATE}", [
    ("input_boolean_turn_on_skip_test",STATE_ON),
    ("input_boolean_turn_off_skip_test",STATE_OFF),
])
async def test_input_boolean_plugin_api_skip(test_context: TstContext, workflow_name: str, initial_state: str):
    entity_id = f"input_boolean.input_boolean_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        input_boolean_provider=INPUT_BOOLEAN_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        input_boolean_entity_id=entity_id,
        input_boolean_entity_state=initial_state
    )

    await test_context.async_start_react([mock_plugin])
        
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()
