import pytest

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_state_test"])
async def test_binary_sensor_state(test_context: TstContext, workflow_name: str):
    
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await vc.async_turn_on("binary_sensor", "binary_sensor_state_test")
        await test_context.hass.async_block_till_done()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["group_state_test"])
async def test_group_state(test_context: TstContext, workflow_name: str):

    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_group()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await vc.async_turn_on("binary_sensor", "group_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_group_state_test"])
async def test_person_group_state(test_context: TstContext, workflow_name: str):
    
    await test_context.async_start_virtual()
    await test_context.async_start_group()
    await test_context.async_start_person()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_react()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await dtc.async_see("person_group_state_test", "home")
        await test_context.hass.async_block_till_done()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker_state_test"])
async def test_device_tracker_state(test_context: TstContext, workflow_name: str):
    
    await test_context.async_start_virtual()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await dtc.async_see("device_tracker_state_test", "home")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()

    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_state_test"])
async def test_person_state(test_context: TstContext, workflow_name: str):
    
    await test_context.async_start_virtual()
    dtc = await test_context.async_start_device_tracker()
    await test_context.async_start_person()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await dtc.async_see("person_state_test", "not_home")
        await test_context.hass.async_block_till_done()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()

    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_state_test"])
async def test_input_number_state(test_context: TstContext, workflow_name: str):
    
    inc = await test_context.async_start_input_number()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await inc.async_set_value("input_number_state_test", 123.45)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_state_test"])
async def test_input_text_state(test_context: TstContext, workflow_name: str):
    
    inc = await test_context.async_start_input_test()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await inc.async_set_value("input_text_state_test", "test_value")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_state_test"])
async def test_input_boolean_state(test_context: TstContext, workflow_name: str):
    
    ibc = await test_context.async_start_input_boolean()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await ibc.async_turn_on("input_boolean_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_button_state_test"])
async def test_input_button_state(test_context: TstContext, workflow_name: str):
    
    ibc = await test_context.async_start_input_button()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await ibc.async_press("input_button_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_state_test"])
async def test_light_state(test_context: TstContext):
    
    await test_context.async_start_virtual()
    lc = await test_context.async_start_light()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await lc.async_turn_on("light_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_state_test"])
async def test_alarm_state(test_context: TstContext, workflow_name: str):
    
    ac = await test_context.async_start_alarm()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await ac.async_arm_away("alarm_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_state_test"])
async def test_switch_state(test_context: TstContext):
    
    await test_context.async_start_virtual()
    sc = await test_context.async_start_switch()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await sc.async_turn_on("switch_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["sensor_state_test"])
async def test_sensor_state(test_context: TstContext):
    
    vc = await test_context.async_start_virtual()
    await test_context.async_start_sensor()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await vc.async_set("sensor", "sensor_state_test", 10)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
    await test_context.hass.async_block_till_done()