import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_ON,
    STATE_OFF,
    STATE_UNKNOWN,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_ENTITY, ATTR_PLUGIN_MODULE, ATTR_STATE, DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_turn_on_test"])
async def test_light_turn_on(hass: HomeAssistant, workflow_name, react_component, light_component):
    """
    Test for light plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.light_plugin_mock"}
    await light_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "light.light_initial_off_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ON)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_turn_off_test"])
async def test_light_turn_off(hass: HomeAssistant, workflow_name, react_component, light_component):
    """
    Test for light plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.light_plugin_mock"}
    await light_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "light.light_initial_on_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_OFF)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_toggle_test"])
async def test_light_toggle(hass: HomeAssistant, workflow_name, react_component, light_component):
    """
    Test for light plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.light_plugin_mock"}
    await light_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "light.light_initial_off_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()

        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ON)
        tc.verify_plugin_data_sent()

        tc.reset()

        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_OFF)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_turn_on_skip_test"])
async def test_light_turn_on_skip(hass: HomeAssistant, workflow_name, react_component, light_component):
    """
    Test for light plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.light_plugin_mock"}
    await light_component
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_turn_off_skip_test"])
async def test_light_turn_off_skip(hass: HomeAssistant, workflow_name, react_component, light_component):
    """
    Test for light plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.light_plugin_mock"}
    await light_component
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
