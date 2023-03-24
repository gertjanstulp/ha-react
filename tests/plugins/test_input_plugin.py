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
async def test_input_number_set(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "input_number.input_number_value_test"
    test_value = 12.34

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value, lambda s: float(s))
        tc.verify_plugin_data_sent()


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
    
    entity_id = "input_number.input_number_value_test"
    test_value = 51.5

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value, lambda s: float(s))
        tc.verify_plugin_data_sent()


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
    
    entity_id = "input_number.input_number_value_test"
    test_value = 51

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value, lambda s: float(s))
        tc.verify_plugin_data_sent()


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
    
    entity_id = "input_number.input_number_value_test"
    test_value = 48.5

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value, lambda s: float(s))
        tc.verify_plugin_data_sent()


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
    
    entity_id = "input_number.input_number_value_test"
    test_value = 49

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value, lambda s: float(s))
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_set_test"])
async def test_input_text_set(hass: HomeAssistant, workflow_name, react_component, input_text_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_text_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "input_text.input_text_value_test"
    test_value = "test_value"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, test_value)
        tc.verify_plugin_data_sent()


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
    
    entity_id = "input_boolean.input_boolean_initial_off_test"

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
    
    entity_id = "input_boolean.input_boolean_initial_on_test"

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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_toggle_test"])
async def test_input_boolean_toggle(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for input plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.input_plugin_mock"}
    await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "input_boolean.input_boolean_initial_off_test"

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
