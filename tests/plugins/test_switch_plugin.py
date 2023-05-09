import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN 
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    STATE_ON,
    STATE_OFF,
)

from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.switch.const import ATTR_SWITCH_PROVIDER

from tests._plugins.switch_mock.plugin import SWITCH_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    switch_entity_id: str = None,
    switch_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if switch_entity_id:
        result[ATTR_ENTITY_ID] = switch_entity_id
    if switch_entity_state != None:
        result[ATTR_ENTITY_STATE] = switch_entity_state


def get_mock_plugin(
    switch_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.switch_mock",
        ATTR_CONFIG: {} 
    }
    if switch_provider:
        result[ATTR_CONFIG][ATTR_SWITCH_PROVIDER] = switch_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_api_turn_on_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_item_set_invalid_entity(test_context, workflow_name, "initial_off")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_api_turn_off_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_item_set_invalid_entity(test_context, workflow_name, "initial_on")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_item_set_invalid_entity(test_context, workflow_name, "initial_off")


async def run_switch_plugin_api_item_set_invalid_entity(test_context: TstContext, workflow_name: str, switch_name: str = "value"):
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
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
        test_context.verify_has_log_record("WARNING", f"Switch plugin: Api - switch.switch_{switch_name}_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_api_turn_on(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_turn_test(test_context, workflow_name, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_api_turn_off(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_turn_test(test_context, workflow_name, STATE_ON, STATE_OFF, STATE_ON)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_on(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_turn_test(test_context, workflow_name, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_off(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_turn_test(test_context, workflow_name, STATE_ON, STATE_OFF, STATE_OFF)


async def run_switch_plugin_api_turn_test(test_context: TstContext, workflow_name: str, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_generic_provider_turn_on(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_generic_provider_turn_test(test_context, workflow_name, STATE_OFF, SERVICE_TURN_ON, STATE_OFF)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_generic_provider_turn_off(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_generic_provider_turn_test(test_context, workflow_name, STATE_ON, SERVICE_TURN_OFF, STATE_ON)


async def run_switch_plugin_generic_provider_turn_test(test_context: TstContext, workflow_name: str, value_before: str, expected_service: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
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
        test_context.verify_service_call_content(SWITCH_DOMAIN, expected_service, data)
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_skip_test"])
async def test_switch_plugin_api_turn_on_skip(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_skip_test(test_context, workflow_name, STATE_ON)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_skip_test"])
async def test_switch_plugin_api_turn_off_skip(test_context: TstContext, workflow_name: str):
    await run_switch_plugin_api_skip_test(test_context, workflow_name, STATE_OFF)


async def run_switch_plugin_api_skip_test(test_context: TstContext, workflow_name: str, initial_state: str):
    entity_id = f"switch.switch_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        switch_entity_id=entity_id,
        switch_entity_state=initial_state
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
