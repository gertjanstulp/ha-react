import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor"])
async def test_react_binary_sensor(hass: HomeAssistant, workflow_name, react_component, input_boolean_component, template_component):
    """
    Test for workflow for a binary_sensor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    comp = await react_component
    await comp.async_setup(workflow_name)
    ibc = await input_boolean_component
    await template_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ibc.async_turn_on("test_binary_sensor")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_group"])
async def test_react_binary_group(hass: HomeAssistant, workflow_name, react_component, template_component, group_component, input_boolean_component):
    """
    Test for workflow for a group:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    ibc = await input_boolean_component
    await template_component
    await group_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ibc.async_turn_on("test_binary_group")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_group"])
async def test_react_person_group(hass: HomeAssistant, workflow_name, react_component, template_component, group_component, input_boolean_component, person_component, device_tracker_component):
    """
    Test for workflow for a group:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await template_component
    await group_component
    await input_boolean_component
    await person_component
    dtc = await device_tracker_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("test_device_tracker", "not_home")
        await dtc.async_see("test_device_tracker", "home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker"])
async def test_react_device_tracker(hass: HomeAssistant, workflow_name, react_component, device_tracker_component):
    """
    Test for workflow for a device_tracker:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    dtc = await device_tracker_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("test_device_tracker", "not_home")
        await dtc.async_see("test_device_tracker", "home")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person"])
async def test_react_person(hass: HomeAssistant, workflow_name, react_component, device_tracker_component, person_component):
    """
    Test for workflow for a person:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    dtc = await device_tracker_component
    await person_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await dtc.async_see("test_device_tracker", "home")
        await dtc.async_see("test_device_tracker", "not_home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_number"])
async def test_react_input_number(hass: HomeAssistant, workflow_name, react_component, input_number_component):
    
    inc = await input_number_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await inc.async_set_value("test_input_number", 123.45)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_text"])
async def test_react_input_text(hass: HomeAssistant, workflow_name, react_component, input_text_component):
    
    inc = await input_text_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await inc.async_set_value("test_input_text", "test_value")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["input_boolean"])
async def test_react_input_boolean(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    
    ibc = await input_boolean_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await ibc.async_turn_on("test_input_boolean")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()
