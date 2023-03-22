import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    ATTR_CODE,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_ENTITY, ATTR_PLUGIN_MODULE, ATTR_STATE, DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT, TEST_FLAG_VERIFY_CONFIG
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_arm_away_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_alarm_arm_away_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_sent(expected_count=0)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_arm_away(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_alarm_arm_away_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "alarm_plugin_test",
        ATTR_CODE: "1234"
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_disarm_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_alarm_disarm_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_sent(expected_count=0)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_disarm(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_alarm_disarm_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "alarm_plugin_test",
        ATTR_CODE: "1234"
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_trigger(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_alarm_trigger_mock"}
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: "alarm_plugin_test",
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
