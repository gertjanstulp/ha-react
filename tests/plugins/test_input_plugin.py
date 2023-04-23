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
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.input.const import INPUT_GENERIC_PROVIDER
from tests._plugins.input_plugin_mock import INPUT_MOCK_PROVIDER

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT
)
from tests.const import ATTR_ENTITY_STATE, ATTR_INPUT_PROVIDER
from tests.tst_context import TstContext


def get_mock_plugin(
    input_provider: str = None,
    input_entity_id: str = None,
    input_entity_state: str = None
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock",
        ATTR_CONFIG: {} 
    }

    if input_provider:
        result[ATTR_CONFIG][ATTR_INPUT_PROVIDER] = input_provider
    if input_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = input_entity_id
    if input_entity_state != None:
        result[ATTR_CONFIG][ATTR_ENTITY_STATE] = input_entity_state

    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_api_number_set_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_number")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_test"])
async def test_input_plugin_api_number_increase_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_number")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_test"])
async def test_input_plugin_api_number_decrease_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_number")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_api_text_set_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_text")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_api_boolean_turn_on_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_boolean", "initial_off")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_api_boolean_turn_off_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_boolean", "initial_on")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "input_boolean", "initial_off")


async def run_input_plugin_api_item_set_invalid_entity(hass: HomeAssistant, workflow_name, react_component, input_type: str, input_name: str = "value"):
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
    )

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
        tc.verify_has_log_record("WARNING", f"Input plugin: Api - {input_type}.{input_type}_{input_name}_test not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_api_number_set(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_number_value_test(hass, workflow_name, react_component, 12.34)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_test"])
async def test_input_plugin_api_number_increase(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_number_value_test(hass, workflow_name, react_component, 51.5)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_with_max_test"])
async def test_input_plugin_api_number_increase_with_max(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_number_value_test(hass, workflow_name, react_component, 51)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_test"])
async def test_input_plugin_api_number_decrease(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_number_value_test(hass, workflow_name, react_component, 48.5)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_with_min_test"])
async def test_input_plugin_api_number_decrease_with_min(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_number_value_test(hass, workflow_name, react_component, 49)


async def run_input_plugin_api_number_value_test(hass: HomeAssistant, workflow_name, react_component, expected_value: Any):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
        input_entity_id=entity_id,
        input_entity_state=50
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        NUMBER_ATTR_VALUE: expected_value,
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
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_api_text_set(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
        input_entity_id=entity_id,
        input_entity_state=50
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        TEXT_ATTR_VALUE: "test_value",
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
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_api_boolean_turn_on(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_set_test(hass, workflow_name, react_component, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_api_boolean_turn_off(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_set_test(hass, workflow_name, react_component, STATE_ON, STATE_OFF, STATE_ON)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_on(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_set_test(hass, workflow_name, react_component, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_plugin_api_boolean_toggle_off(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_set_test(hass, workflow_name, react_component, STATE_ON, STATE_OFF, STATE_OFF)


async def run_input_plugin_api_boolean_set_test(hass: HomeAssistant, workflow_name, react_component, value_before: str, value_after: str, name_initial: str):
    entity_id = f"input_boolean.input_boolean_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
        input_entity_id=entity_id,
        input_entity_state=value_before
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_STATE: value_after,
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
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(data)
    

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_plugin_generic_provider_number_set(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin(
        input_entity_id=entity_id,
        input_entity_state=50
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        NUMBER_ATTR_VALUE: 12.34,
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
        tc.verify_service_call_content(NUMBER_DOMAIN, NUMBER_SERVICE_SET_VALUE, data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_plugin_generic_provider_text_set(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "input_text.input_text_value_test"
    mock_plugin = get_mock_plugin(
        input_entity_id=entity_id,
        input_entity_state=""
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        TEXT_ATTR_VALUE: "test_value",
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
        tc.verify_service_call_content(TEXT_DOMAIN,  TEXT_SERVICE_SET_VALUE, data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_plugin_generic_provider_boolean_turn_on(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_generic_provider_boolean_set_test(hass, workflow_name, react_component, STATE_OFF, STATE_ON, SERVICE_TURN_ON)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_plugin_generic_provider_boolean_turn_off(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_generic_provider_boolean_set_test(hass, workflow_name, react_component, STATE_ON, STATE_OFF, SERVICE_TURN_OFF)


async def run_input_plugin_generic_provider_boolean_set_test(hass: HomeAssistant, workflow_name, react_component, value_before: str, value_after: str, expected_service: str):
    entity_id = f"input_boolean.input_boolean_initial_{value_before}_test"
    mock_plugin = get_mock_plugin(
        input_entity_id=entity_id,
        input_entity_state=value_before
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
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
        tc.verify_service_call_content(BOOLEAN_DOMAIN, expected_service, data)
    

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_skip_test"])
async def test_input_plugin_api_boolean_turn_on_skip(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_skip_test(hass, workflow_name, react_component, STATE_ON)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_skip_test"])
async def test_input_plugin_api_boolean_turn_off_skip(hass: HomeAssistant, workflow_name, react_component):
    await run_input_plugin_api_boolean_skip_test(hass, workflow_name, react_component, STATE_OFF)


async def run_input_plugin_api_boolean_skip_test(hass: HomeAssistant, workflow_name, react_component, initial_state: str):
    entity_id = f"input_boolean.input_boolean_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        input_provider=INPUT_MOCK_PROVIDER,
        input_entity_id=entity_id,
        input_entity_state=initial_state
    )

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
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_not_sent()
