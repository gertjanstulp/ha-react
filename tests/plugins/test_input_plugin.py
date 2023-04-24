from typing import Any
import pytest

from homeassistant.components.input_boolean import (
    DOMAIN as BOOLEAN_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.components.input_number import (
    ATTR_VALUE as NUMBER_ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE as NUMBER_SERVICE_SET_VALUE,
)
from homeassistant.components.input_text import (
    DOMAIN as TEXT_DOMAIN,
    SERVICE_SET_VALUE as TEXT_SERVICE_SET_VALUE,
    ATTR_VALUE as TEXT_ATTR_VALUE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.input.const import ATTR_INPUT_PROVIDER
from tests._plugins.input_mock.plugin import INPUT_MOCK_PROVIDER

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import ATTR_ENTITY_STATE, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    input_entity_id: str = None,
    input_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if input_entity_id:
        result[ATTR_ENTITY_ID] = input_entity_id
    if input_entity_state != None:
        result[ATTR_ENTITY_STATE] = input_entity_state


def get_mock_plugin(
    input_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_mock",
        ATTR_CONFIG: {} 
    }
    if input_provider:
        result[ATTR_CONFIG][ATTR_INPUT_PROVIDER] = input_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_api_number_set_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_number")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_test"])
async def test_input_plugin_api_number_increase_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_number")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_test"])
async def test_input_plugin_api_number_decrease_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_number")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_api_text_set_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_text")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_api_boolean_turn_on_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_boolean", "initial_off")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_api_boolean_turn_off_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_boolean", "initial_on")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_item_set_invalid_entity(test_context, workflow_name, "input_boolean", "initial_off")


async def run_input_plugin_api_item_set_invalid_entity(test_context: TstContext, workflow_name: str, input_type: str, input_name: str = "value"):
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
    )

    await test_context.async_start_react(mock_plugin)
        
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_plugin_data_not_sent()
        test_context.verify_has_log_record("WARNING", f"Input plugin: Api - {input_type}.{input_type}_{input_name}_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_api_number_set(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_number_value_test(test_context, workflow_name, 12.34)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_test"])
async def test_input_plugin_api_number_increase(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_number_value_test(test_context, workflow_name, 51.5)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_with_max_test"])
async def test_input_plugin_api_number_increase_with_max(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_number_value_test(test_context, workflow_name, 51)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_test"])
async def test_input_plugin_api_number_decrease(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_number_value_test(test_context, workflow_name, 48.5)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_with_min_test"])
async def test_input_plugin_api_number_decrease_with_min(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_number_value_test(test_context, workflow_name, 49)


async def run_input_plugin_api_number_value_test(test_context: TstContext, workflow_name: str, expected_value: Any):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=50
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        NUMBER_ATTR_VALUE: expected_value,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_api_text_set(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=50
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        TEXT_ATTR_VALUE: "test_value",
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_api_boolean_turn_on(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_set_test(test_context, workflow_name, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_api_boolean_turn_off(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_set_test(test_context, workflow_name, STATE_ON, STATE_OFF, STATE_ON)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_on(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_set_test(test_context, workflow_name, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_off(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_set_test(test_context, workflow_name, STATE_ON, STATE_OFF, STATE_OFF)


async def run_input_plugin_api_boolean_set_test(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):
    entity_id = f"input_boolean.input_boolean_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=value_before
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(data)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_generic_provider_number_set(test_context: TstContext, workflow_name: str):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=50
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        NUMBER_ATTR_VALUE: 12.34,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(NUMBER_DOMAIN, NUMBER_SERVICE_SET_VALUE, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_generic_provider_text_set(test_context: TstContext, workflow_name: str):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=""
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
        TEXT_ATTR_VALUE: "test_value",
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(TEXT_DOMAIN,  TEXT_SERVICE_SET_VALUE, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_generic_provider_boolean_turn_on(test_context: TstContext, workflow_name: str):
    await run_input_plugin_generic_provider_boolean_set_test(test_context, workflow_name, STATE_OFF, STATE_ON, SERVICE_TURN_ON)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_generic_provider_boolean_turn_off(test_context: TstContext, workflow_name: str):
    await run_input_plugin_generic_provider_boolean_set_test(test_context, workflow_name, STATE_ON, STATE_OFF, SERVICE_TURN_OFF)


async def run_input_plugin_generic_provider_boolean_set_test(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, expected_service: str):
    entity_id = f"input_boolean.input_boolean_initial_{value_before}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=value_before
    )

    await test_context.async_start_react(mock_plugin)
        
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(BOOLEAN_DOMAIN, expected_service, data)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_skip_test"])
async def test_input_plugin_api_boolean_turn_on_skip(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_skip_test(test_context, workflow_name, STATE_ON)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_skip_test"])
async def test_input_plugin_api_boolean_turn_off_skip(test_context: TstContext, workflow_name: str):
    await run_input_plugin_api_boolean_skip_test(test_context, workflow_name, STATE_OFF)


async def run_input_plugin_api_boolean_skip_test(test_context: TstContext, workflow_name: str, initial_state: str):
    entity_id = f"input_boolean.input_boolean_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        input_entity_id=entity_id,
        input_entity_state=initial_state
    )

    await test_context.async_start_react(mock_plugin)
        
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_not_sent()
