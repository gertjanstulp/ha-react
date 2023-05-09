import pytest

from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
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

from custom_components.react.const import (
    ATTR_MODE,
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.alarm.const import ATTR_ALARM_PROVIDER, ArmMode
from custom_components.react.plugin.const import ATTR_CONFIG

from tests._plugins.alarm_mock.plugin import (
    ALARM_MOCK_PROVIDER, 
    ATTR_ALARM_STATE
)
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext

ALARM_CODE = "1234"


def set_test_config(test_context: TstContext,
    alarm_entity_id: str = None,
    alarm_state: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if alarm_entity_id:
        result[ATTR_ENTITY_ID] = alarm_entity_id
    if alarm_state:
        result[ATTR_ALARM_STATE] = alarm_state
        

def get_mock_plugin(
    code: str = None, 
    alarm_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.alarm_mock",
        ATTR_CONFIG: {} 
    }
    if code:
        result[ATTR_CONFIG][ATTR_CODE] = code
    if alarm_provider:
        result[ATTR_CONFIG][ATTR_ALARM_PROVIDER] = alarm_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_invalid_config(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_config(test_context)


async def run_alarm_plugin_api_arm_invalid_config(test_context: TstContext):
    await test_context.async_start_react(get_mock_plugin())

    async with test_context.async_listen_reaction_event():
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_plugin_data_not_sent()
        test_context.verify_has_log_record("ERROR", "Configuration for tests._plugins.alarm_mock is invalid - required key not provided: code")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_entity(test_context, workflow_name)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_entity(test_context, workflow_name)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_entity(test_context, workflow_name)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_entity(test_context, workflow_name)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_invalid_entity(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_entity(test_context, workflow_name)


async def run_alarm_plugin_api_arm_invalid_entity(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_plugin_data_not_sent()
        test_context.verify_has_log_record("WARNING", "Alarm plugin: Api - alarm_control_panel.alarm_plugin_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm(test_context, workflow_name, ArmMode.HOME)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm(test_context, workflow_name, ArmMode.AWAY)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm(test_context, workflow_name, ArmMode.NIGHT)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm(test_context, workflow_name, ArmMode.VACATION)


async def run_alarm_plugin_api_arm(test_context: TstContext, workflow_name: str, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react(mock_plugin)

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
        ATTR_MODE: expected_arm_mode,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(data, 0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_api_arm_home_when_not_disarmed(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_when_not_disarmed(test_context, workflow_name, ArmMode.HOME)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_arm_away_when_not_disarmed(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_when_not_disarmed(test_context, workflow_name, ArmMode.AWAY)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_api_arm_night_when_not_disarmed(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_when_not_disarmed(test_context, workflow_name, ArmMode.NIGHT)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_api_arm_vacation_when_not_disarmed(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_when_not_disarmed(test_context, workflow_name, ArmMode.VACATION)


async def run_alarm_plugin_api_arm_when_not_disarmed(test_context: TstContext, workflow_name: str, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_home_test"])
async def test_alarm_plugin_generic_provider_arm_home(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_generic_provider_arm(test_context, workflow_name, SERVICE_ALARM_ARM_HOME)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_generic_provider_arm_away(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_generic_provider_arm(test_context, workflow_name, SERVICE_ALARM_ARM_AWAY)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_night_test"])
async def test_alarm_plugin_generic_provider_arm_night(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_generic_provider_arm(test_context, workflow_name, SERVICE_ALARM_ARM_NIGHT)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_vacation_test"])
async def test_alarm_plugin_generic_provider_arm_vacation(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_generic_provider_arm(test_context, workflow_name, SERVICE_ALARM_ARM_VACATION)
    

async def run_alarm_plugin_generic_provider_arm(test_context: TstContext, workflow_name: str, expected_arm_service: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react(mock_plugin)
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(ALARM_DOMAIN, expected_arm_service, data, 0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_when_not_armed(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    await test_context.async_start_react(mock_plugin)

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_generic_provider_disarm(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    await test_context.async_start_react(mock_plugin)
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_DISARM, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_api_trigger(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
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
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_generic_provider_trigger(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
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
        test_context.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_TRIGGER, data)
