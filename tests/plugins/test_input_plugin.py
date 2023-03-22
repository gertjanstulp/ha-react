import pytest

from homeassistant.core import HomeAssistant
from homeassistant.components.input_number import (
    ATTR_VALUE as NUMBER_ATTR_VALUE
)
from homeassistant.components.input_text import (
    ATTR_VALUE as TEXT_ATTR_VALUE
)
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_set_test"])
async def test_input_number_set(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_number.input_number_set_test",
        NUMBER_ATTR_VALUE: 12.34
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_test"])
async def test_input_number_increase(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_number.input_number_increase_test",
        NUMBER_ATTR_VALUE: 51.5
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_increase_with_max_test"])
async def test_input_number_increase_with_max(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_number.input_number_increase_test",
        NUMBER_ATTR_VALUE: 51
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_test"])
async def test_input_number_decrease(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_number.input_number_decrease_test",
        NUMBER_ATTR_VALUE: 48.5
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_decrease_with_min_test"])
async def test_input_number_decrease_with_min(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_number.input_number_decrease_test",
        NUMBER_ATTR_VALUE: 49
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_set(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_text.input_text_set_test",
        TEXT_ATTR_VALUE: "test_value"
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_test"])
async def test_input_boolean_turn_on(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_boolean.input_boolean_turn_on_test",
        ATTR_STATE: STATE_ON
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_test"])
async def test_input_boolean_turn_off(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_boolean.input_boolean_turn_off_test",
        ATTR_STATE: STATE_OFF
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_on_test"])
async def test_input_boolean_toggle_on(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_boolean.input_boolean_toggle_on_test",
        ATTR_STATE: STATE_ON
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_off_test"])
async def test_input_boolean_toggle_off(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "input_boolean.input_boolean_toggle_off_test",
        ATTR_STATE: STATE_OFF
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_on_skip_test"])
async def test_input_boolean_turn_on_skip(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_turn_off_skip_test"])
async def test_input_boolean_turn_off_skip(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
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
