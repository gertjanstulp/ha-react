from asyncio import sleep
import pytest

from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_CODE,
    ATTR_ENTITY_ID,
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_ARM_HOME,
    SERVICE_ALARM_ARM_NIGHT,
    SERVICE_ALARM_ARM_VACATION,
    SERVICE_ALARM_DISARM,
    SERVICE_ALARM_TRIGGER,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_MODE,
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)
from custom_components.react.plugin.alarm.const import ArmMode
from custom_components.react.plugin.const import ATTR_CONFIG

from tests._plugins.alarm_plugin_mock import (
    ALARM_MOCK_PROVIDER, 
    ATTR_ALARM_STATE
)
from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT, 
)
from tests.const import ATTR_ALARM_PROVIDER
from tests.tst_context import TstContext


ALARM_CODE = "1234"


def get_mock_plugin(
    code: str = None, 
    alarm_provider: str = None,
    alarm_entity_id: str = None,
    alarm_state: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.alarm_plugin_mock",
        ATTR_CONFIG: {} 
    }

    if code:
        result[ATTR_CONFIG][ATTR_CODE] = code
    if alarm_provider:
        result[ATTR_CONFIG][ATTR_ALARM_PROVIDER] = alarm_provider
    if alarm_entity_id:
        result[ATTR_CONFIG][ATTR_ENTITY_ID] = alarm_entity_id
    if alarm_state:
        result[ATTR_CONFIG][ATTR_ALARM_STATE] = alarm_state
    
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_config(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_config(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_config(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_config(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_config(hass, workflow_name, react_component)


async def run_alarm_plugin_api_arm_invalid_config(hass: HomeAssistant, workflow_name, react_component):
    mock_plugin = get_mock_plugin()

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_not_sent()
        tc.verify_has_log_record("ERROR", "Alarm plugin: Api - No code configured")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_entity(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_entity(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_entity(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_entity(hass, workflow_name, react_component)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_invalid_entity(hass, workflow_name, react_component)


async def run_alarm_plugin_api_arm_invalid_entity(hass: HomeAssistant, workflow_name, react_component):
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_plugin_data_not_sent()
        tc.verify_has_log_record("WARNING", "Alarm plugin: Api - alarm_control_panel.alarm_plugin_test not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm(hass, workflow_name, react_component, ArmMode.HOME)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm(hass, workflow_name, react_component, ArmMode.AWAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm(hass, workflow_name, react_component, ArmMode.NIGHT)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm(hass, workflow_name, react_component, ArmMode.VACATION)


async def run_alarm_plugin_api_arm(hass: HomeAssistant, workflow_name, react_component, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
        ATTR_MODE: expected_arm_mode,
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
        tc.verify_plugin_data_content(data, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home_when_not_disarmed(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_when_not_disarmed(hass, workflow_name, react_component, ArmMode.HOME)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away_when_not_disarmed(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_when_not_disarmed(hass, workflow_name, react_component, ArmMode.AWAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night_when_not_disarmed(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_when_not_disarmed(hass, workflow_name, react_component, ArmMode.NIGHT)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation_when_not_disarmed(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_api_arm_when_not_disarmed(hass, workflow_name, react_component, ArmMode.VACATION)


async def run_alarm_plugin_api_arm_when_not_disarmed(hass: HomeAssistant, workflow_name, react_component, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_generic_provider_arm_home(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_generic_provider_arm(hass, workflow_name, react_component, SERVICE_ALARM_ARM_HOME)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_generic_provider_arm_away(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_generic_provider_arm(hass, workflow_name, react_component, SERVICE_ALARM_ARM_AWAY)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_generic_provider_arm_night(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_generic_provider_arm(hass, workflow_name, react_component, SERVICE_ALARM_ARM_NIGHT)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_generic_provider_arm_vacation(hass: HomeAssistant, workflow_name, react_component):
    await run_alarm_plugin_generic_provider_arm(hass, workflow_name, react_component, SERVICE_ALARM_ARM_VACATION)
    

async def run_alarm_plugin_generic_provider_arm(hass: HomeAssistant, workflow_name, react_component, expected_arm_service: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
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
        tc.verify_service_call_content(ALARM_DOMAIN, expected_arm_service, data, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_when_not_armed(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
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


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
    }

    tc = react.hass.data[TEST_CONTEXT] = TstContext(hass, workflow_name)
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_generic_provider_disarm(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
    }

    tc = react.hass.data[TEST_CONTEXT] = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_DISARM, data)


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_api_trigger(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    tc = react.hass.data[TEST_CONTEXT] = TstContext(hass, workflow_name)
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
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_generic_provider_trigger(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    tc = react.hass.data[TEST_CONTEXT] = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_TRIGGER, data)
