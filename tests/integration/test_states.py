import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor"])
async def test_react_binary_sensor(hass: HomeAssistant, workflow_name, react_component, input_boolean_component, template_component):
    """
    Test for workflow for a binary_sensor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await input_boolean_component.async_turn_on("test_binary_sensor")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_group"])
async def test_react_binary_group(hass: HomeAssistant, workflow_name, react_component, template_component, group_component, input_boolean_component):
    """
    Test for workflow for a group:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await input_boolean_component.async_turn_on("test_binary_group")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person_group"])
async def test_react_person_group(hass: HomeAssistant, workflow_name, react_component, template_component, group_component, input_boolean_component, person_component, device_tracker_component):
    """
    Test for workflow for a group:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await device_tracker_component.async_see("test_device_tracker", "not_home")
        await device_tracker_component.async_see("test_device_tracker", "home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["device_tracker"])
async def test_react_device_tracker(hass: HomeAssistant, workflow_name, react_component, device_tracker_component):
    """
    Test for workflow for a device_tracker:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await device_tracker_component.async_see("test_device_tracker", "not_home")
        await device_tracker_component.async_see("test_device_tracker", "home")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["person"])
async def test_react_person(hass: HomeAssistant, workflow_name, react_component, device_tracker_component, person_component):
    """
    Test for workflow for a person:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await device_tracker_component.async_see("test_device_tracker", "home")
        await device_tracker_component.async_see("test_device_tracker", "not_home")
        await hass.async_block_till_done()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

    await hass.async_block_till_done()