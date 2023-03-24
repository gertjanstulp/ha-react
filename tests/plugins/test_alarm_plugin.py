from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_CODE,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED
)

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)

from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT, 
    TEST_FLAG_VERIFY_CONFIG
)
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_arm_home_invalid_config(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_DISARMED)
        tc.verify_plugin_data_not_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_arm_home(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock", "config": { ATTR_CODE: '1234'}}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_ARMING)
        await sleep(1.1)
        tc.verify_state(entity_id, STATE_ALARM_ARMED_HOME)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_arm_away_invalid_config(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_DISARMED)
        tc.verify_plugin_data_not_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_arm_away(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock", "config": { ATTR_CODE: '1234'}}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_ARMING)
        await sleep(1.1)
        tc.verify_state(entity_id, STATE_ALARM_ARMED_AWAY)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_arm_night_invalid_config(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_DISARMED)
        tc.verify_plugin_data_not_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_arm_night(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock", "config": { ATTR_CODE: '1234'}}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_ARMING)
        await sleep(1.1)
        tc.verify_state(entity_id, STATE_ALARM_ARMED_NIGHT)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_arm_vacation_invalid_config(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    react.hass.data[TEST_FLAG_VERIFY_CONFIG] = False
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_DISARMED)
        tc.verify_plugin_data_not_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_arm_vacation(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock", "config": { ATTR_CODE: '1234'}}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_ARMING)
        await sleep(1.1)
        tc.verify_state(entity_id, STATE_ALARM_ARMED_VACATION)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_disarm_invalid_config(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
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
async def test_alarm_plugin_disarm(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    code = '1234'
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock", "config": { ATTR_CODE: code}}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    await tc.async_arm_alarm(entity_id, code)
    await sleep(1.1)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_DISARMED)
        tc.verify_plugin_data_sent()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_trigger(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    """
    Test for alarm plugin
    """

    code = '1234'
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock"}
    await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    entity_id = "alarm_control_panel.alarm_plugin_test"

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    await tc.async_arm_alarm(entity_id, code)
    await sleep(1.1)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_state(entity_id, STATE_ALARM_PENDING)
        await sleep(1.5)
        tc.verify_state(entity_id, STATE_ALARM_TRIGGERED)
        tc.verify_plugin_data_sent()
