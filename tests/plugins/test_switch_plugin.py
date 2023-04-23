import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN 
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_PLUGIN_MODULE,
    ATTR_STATE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from tests._plugins.switch_plugin_mock import SWITCH_MOCK_PROVIDER

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT
)
from tests.const import ATTR_ENTITY_STATE, ATTR_SWITCH_PROVIDER
from tests.tst_context import TstContext


def get_mock_plugin(
    switch_provider: str = None,
    switch_entity_id: str = None,
    switch_entity_state: str = None
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.switch_plugin_mock",
        ATTR_CONFIG: {} 
    }

    if switch_provider:
        result[ATTR_CONFIG][ATTR_SWITCH_PROVIDER] = switch_provider
    if switch_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = switch_entity_id
    if switch_entity_state != None:
        result[ATTR_CONFIG][ATTR_ENTITY_STATE] = switch_entity_state

    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_api_turn_on_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "initial_off")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_api_turn_off_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "initial_on")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_item_set_invalid_entity(hass, workflow_name, react_component, "initial_off")


async def run_switch_plugin_api_item_set_invalid_entity(hass: HomeAssistant, workflow_name, react_component, switch_name: str = "value"):
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
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
        tc.verify_has_log_record("WARNING", f"Switch plugin: Api - switch.switch_{switch_name}_test not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_api_turn_on(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_turn_test(hass, workflow_name, react_component, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_api_turn_off(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_turn_test(hass, workflow_name, react_component, STATE_ON, STATE_OFF, STATE_ON)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_on(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_turn_test(hass, workflow_name, react_component, STATE_OFF, STATE_ON, STATE_OFF)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_toggle_test"])
async def test_switch_plugin_api_toggle_off(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_turn_test(hass, workflow_name, react_component, STATE_ON, STATE_OFF, STATE_OFF)


async def run_switch_plugin_api_turn_test(hass: HomeAssistant, workflow_name, react_component, value_before: str, value_after: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
        switch_entity_id=entity_id,
        switch_entity_state=value_before
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_test"])
async def test_switch_plugin_generic_provider_turn_on(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_generic_provider_turn_test(hass, workflow_name, react_component, STATE_OFF, SERVICE_TURN_ON, STATE_OFF)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_test"])
async def test_switch_plugin_generic_provider_turn_off(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_generic_provider_turn_test(hass, workflow_name, react_component, STATE_ON, SERVICE_TURN_OFF, STATE_ON)


async def run_switch_plugin_generic_provider_turn_test(hass: HomeAssistant, workflow_name, react_component, value_before: str, expected_service: str, name_initial: str):    
    entity_id = f"switch.switch_initial_{name_initial}_test"
    mock_plugin = get_mock_plugin(
        switch_entity_id=entity_id,
        switch_entity_state=value_before
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
        tc.verify_service_call_content(SWITCH_DOMAIN, expected_service, data)
    

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_on_skip_test"])
async def test_switch_plugin_api_turn_on_skip(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_skip_test(hass, workflow_name, react_component, STATE_ON)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_turn_off_skip_test"])
async def test_switch_plugin_api_turn_off_skip(hass: HomeAssistant, workflow_name, react_component):
    await run_switch_plugin_api_skip_test(hass, workflow_name, react_component, STATE_OFF)


async def run_switch_plugin_api_skip_test(hass: HomeAssistant, workflow_name, react_component, initial_state: str):
    entity_id = f"switch.switch_initial_{initial_state}_test"
    mock_plugin = get_mock_plugin(
        switch_provider=SWITCH_MOCK_PROVIDER,
        switch_entity_id=entity_id,
        switch_entity_state=initial_state
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
