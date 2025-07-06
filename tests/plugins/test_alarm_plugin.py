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
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMED,
)

from custom_components.react.const import (
    ACTION_CHANGE,
    ATTR_MODE,
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.alarm_control_panel.const import ATTR_ALARM_PROVIDER, ArmMode
from custom_components.react.plugin.const import ATTR_CONFIG

from tests._plugins.alarm_mock.setup import (
    ALARM_MOCK_PROVIDER, 
    ATTR_ALARM_STATE
)
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import ALARM_CODE, ATTR_SETUP_MOCK_PROVIDER, TEST_CONFIG
from tests.tst_context import TstContext

FIXTURE_EXPECTED_ARM_MODE = "expected_arm_mode"
FIXTURE_EXPECTED_ARM_SERVICE = "expected_arm_service"


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    alarm_entity_id: str = None,
    alarm_state: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if alarm_entity_id:
        result[ATTR_ENTITY_ID] = alarm_entity_id
    if alarm_state:
        result[ATTR_ALARM_STATE] = alarm_state
        

def get_mock_plugin(
    code: str = None, 
    alarm_control_panel_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.alarm_mock",
        ATTR_CONFIG: {} 
    }
    if code:
        result[ATTR_CONFIG][ATTR_CODE] = code
    if alarm_control_panel_provider:
        result[ATTR_CONFIG][ATTR_ALARM_PROVIDER] = alarm_control_panel_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_invalid_config(test_context: TstContext, workflow_name: str):
    await run_alarm_plugin_api_arm_invalid_config(test_context)


async def run_alarm_plugin_api_arm_invalid_config(test_context: TstContext):
    mock_plugin = get_mock_plugin()
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error("Configuration for tests._plugins.alarm_mock is invalid - required key not provided: code")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [
    "alarm_plugin_arm_home_test", 
    "alarm_plugin_arm_away_test", 
    "alarm_plugin_arm_night_test", 
    "alarm_plugin_arm_vacation_test", 
    "alarm_plugin_disarm_test"
])
async def test_alarm_plugin_api_invalid_entity(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning("1 - alarm_control_panel.alarm_plugin_test not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_arm_away_test"])
async def test_alarm_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state="test"
    )
    
    data = {
        ATTR_ALARM_PROVIDER: invalid_provider
    }
    
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Alarm_control_panel provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_ARM_MODE}", [
    ("alarm_plugin_arm_home_test", ArmMode.HOME), 
    ("alarm_plugin_arm_away_test", ArmMode.AWAY), 
    ("alarm_plugin_arm_night_test", ArmMode.NIGHT), 
    ("alarm_plugin_arm_vacation_test", ArmMode.VACATION)
])
async def test_alarm_plugin_api_arm_config_provider(test_context: TstContext, workflow_name: str, expected_arm_mode: ArmMode, socket_enabled):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_control_panel_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react([mock_plugin])

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
        ATTR_MODE: expected_arm_mode,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data, 0)


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_ARM_MODE}", [
    ("alarm_plugin_arm_home_test", ArmMode.HOME), 
    ("alarm_plugin_arm_away_test", ArmMode.AWAY), 
    ("alarm_plugin_arm_night_test", ArmMode.NIGHT), 
    ("alarm_plugin_arm_vacation_test", ArmMode.VACATION)
])
async def test_alarm_plugin_api_arm_event_provider(test_context: TstContext, workflow_name: str, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react([mock_plugin])

    data_in = {
        ATTR_ALARM_PROVIDER: ALARM_MOCK_PROVIDER
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
        ATTR_MODE: expected_arm_mode,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out, 0)


@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_ARM_MODE}", [
    ("alarm_plugin_arm_home_test", ArmMode.HOME), 
    ("alarm_plugin_arm_away_test", ArmMode.AWAY),
    ("alarm_plugin_arm_night_test", ArmMode.NIGHT),
    ("alarm_plugin_arm_vacation_test", ArmMode.VACATION)
])
async def test_alarm_plugin_api_arm_when_not_disarmed(test_context: TstContext, workflow_name: str, expected_arm_mode: ArmMode):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_control_panel_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()
    
    
@pytest.mark.parametrize(f"{FIXTURE_WORKFLOW_NAME},{FIXTURE_EXPECTED_ARM_SERVICE}", [
    ("alarm_plugin_arm_home_test", SERVICE_ALARM_ARM_HOME),
    ("alarm_plugin_arm_away_test", SERVICE_ALARM_ARM_AWAY),
    ("alarm_plugin_arm_night_test", SERVICE_ALARM_ARM_NIGHT),
    ("alarm_plugin_arm_vacation_test", SERVICE_ALARM_ARM_VACATION),
])
async def test_alarm_plugin_generic_provider_arm(test_context: TstContext, workflow_name: str, expected_arm_service: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    set_test_config(test_context,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react([mock_plugin])
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(ALARM_DOMAIN, expected_arm_service, data, 0)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm_when_not_armed(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_control_panel_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_DISARMED
    )

    await test_context.async_start_react([mock_plugin])
    
    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_not_sent()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_disarm_test"])
async def test_alarm_plugin_api_disarm(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_control_panel_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    await test_context.async_start_react([mock_plugin])

    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
    }

    await test_context.async_send_reaction_event()
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

    await test_context.async_start_react([mock_plugin])
    
    data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_CODE: ALARM_CODE
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_DISARM, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_plugin_trigger_test"])
async def test_alarm_plugin_api_trigger(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_control_panel.alarm_plugin_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
        alarm_control_panel_provider=ALARM_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        alarm_entity_id=entity_id,
        alarm_state=STATE_ALARM_ARMED_HOME
    )

    await test_context.async_start_react([mock_plugin])
    
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event()
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

    await test_context.async_start_react([mock_plugin])
    
    data = {
        ATTR_ENTITY_ID: entity_id,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(ALARM_DOMAIN, SERVICE_ALARM_TRIGGER, data)



@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_state_test"])
async def test_alarm_plugin_input_block_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "alarm_state_test"
    mock_plugin = get_mock_plugin(
        code=ALARM_CODE, 
    )
    ac = await test_context.async_start_alarm()
    await test_context.async_start_react([mock_plugin])
    
    async with test_context.async_listen_action_event():
        await ac.async_arm_away(entity_id)
        await test_context.async_verify_action_event_received(expected_count=3)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=ALARM_DOMAIN,
            expected_action=ACTION_CHANGE,
            event_with_action_name=ACTION_CHANGE)
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=ALARM_DOMAIN,
            expected_action=f"un_{STATE_ALARM_DISARMED}",
            event_with_action_name=f"un_{STATE_ALARM_DISARMED}")
        test_context.verify_action_event_data(
            expected_entity=entity_id,
            expected_type=ALARM_DOMAIN,
            expected_action=f"{STATE_ALARM_ARMED_AWAY}",
            event_with_action_name=f"{STATE_ALARM_ARMED_AWAY}")
        test_context.verify_has_no_log_issues()
    await test_context.hass.async_block_till_done()
