import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_state_test"])
async def test_binary_sensor_state(hass: HomeAssistant, workflow_name, react_component, virtual_component, binary_sensor_component):
    
    vc = await virtual_component
    await binary_sensor_component
    rc = await react_component
    await rc.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await vc.async_turn_on("binary_sensor", "binary_sensor_state_test")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["group_state_test"])
async def test_group_state(hass: HomeAssistant, workflow_name, react_component, virtual_component, binary_sensor_component, group_component):
    """
    Test for workflow for a group:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    vc = await virtual_component
    await binary_sensor_component
    await group_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await vc.async_turn_on("binary_sensor", "group_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_group_state_test"])
async def test_person_group_state(hass: HomeAssistant, workflow_name, react_component, virtual_component, group_component, person_component, device_tracker_component):
    
    await virtual_component
    await group_component
    await person_component
    dtc = await device_tracker_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("person_group_state_test", "home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker_state_test"])
async def test_device_tracker_state(hass: HomeAssistant, workflow_name, react_component, virtual_component, device_tracker_component):
    
    await virtual_component
    dtc = await device_tracker_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("device_tracker_state_test", "home")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_state_test"])
async def test_person_state(hass: HomeAssistant, workflow_name, react_component, virtual_component, device_tracker_component, person_component):
    
    await virtual_component
    dtc = await device_tracker_component
    await person_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("person_state_test", "not_home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number_state_test"])
async def test_input_number_state(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    
    inc = await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await inc.async_set_value("input_number_state_test", 123.45)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text_state_test"])
async def test_input_text_state(hass: HomeAssistant, workflow_name, react_component, input_text_component):
    
    inc = await input_text_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await inc.async_set_value("input_text_state_test", "test_value")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean_state_test"])
async def test_input_boolean_state(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    
    ibc = await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ibc.async_turn_on("input_boolean_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_button_state_test"])
async def test_input_button_state(hass: HomeAssistant, workflow_name, react_component, input_button_component):
    
    ibc = await input_button_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ibc.async_press("input_button_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["light_state_test"])
async def test_light_state(hass: HomeAssistant, workflow_name, virtual_component, react_component, light_component):
    
    vc = await virtual_component
    lc = await light_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await lc.async_turn_on("light_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["alarm_state_test"])
async def test_alarm_state(hass: HomeAssistant, workflow_name, react_component, alarm_component):
    
    ac = await alarm_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ac.async_arm_away("alarm_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["switch_state_test"])
async def test_switch_state(hass: HomeAssistant, workflow_name, virtual_component, react_component, switch_component):
    
    await virtual_component
    sc = await switch_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await sc.async_turn_on("switch_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["sensor_state_test"])
async def test_sensor_state(hass: HomeAssistant, workflow_name, virtual_component, react_component, sensor_component):
    
    vc = await virtual_component
    await sensor_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await vc.async_set("sensor", "sensor_state_test", 10)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()