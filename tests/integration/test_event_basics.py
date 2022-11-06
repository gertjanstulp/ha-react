from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

FIXTURE_ADDITIONAL_TESTS = "additional_tests"


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["immediate"])
async def test_react_immediate(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with immediate reactor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed"])
async def test_react_delayed(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with delayed reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - An event should be sent after a configured delay
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        await tc.async_verify_reaction_event_received(delay=6)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
        tc.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_react_scheduled(hass: HomeAssistant, workflow_name, react_component):
    """ 
    Test for workflow with scheduled reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        tc.verify_trace_record(expected_event_trace=False)
        await tc.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reset"])
async def test_react_reset(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with reset reactor:
    - Reactions should be found before sending reset event
    - No reactions should be found after sending reset event
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name, ["delayed", "scheduled"])

    tc = TstContext(hass, workflow_name)
    tc_delayed = TstContext(hass, "delayed")
    tc_scheduled = TstContext(hass, "scheduled")

    async with tc_delayed.async_listen_react_event():
        await tc_delayed.async_send_action_event()
    async with tc_scheduled.async_listen_react_event():
        await tc_scheduled.async_send_action_event()

    async with tc.async_listen_react_event():
        tc.verify_reaction_found(2)
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        tc.verify_trace_record()

    await tc_delayed.async_stop_all_runs()
    await tc_scheduled.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_action"])
async def test_react_forward_action_no_toggle(hass: HomeAssistant, workflow_name, react_component):
    """ 
    Test for workflow with reactor with forwardaction and not event action 'toggle':
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration and forwarded action
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(action="test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_action="test")
        tc.verify_trace_record(expected_runtime_actor_action="test")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_action"])
async def test_react_forward_action_toggle(hass: HomeAssistant, workflow_name, react_component):
    """ 
    Test for workflow with reactor with forwardaction and event action 'toggle':
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(action="toggle")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_trace_record(expected_result_message="Skipped, toggle with forward-action")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_data"])
async def test_react_forward_data(hass: HomeAssistant, workflow_name, react_component):
    """ 
    Test for workflow with reactor with forwarddata :
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration and forwarded data
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    data_in: dict = {
        "data1" : 37,
        "data2": ["asdf", "qwer"],
    }

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_in)
        tc.verify_trace_record(expected_runtime_reactor_data=data_in)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["full_stencil"])
async def test_react_full_stencil(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with full stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    data_out: dict = {
        "test": 37
    }
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_data=data_out)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["partial_stencil"])
async def test_react_partial_stencil(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with partial stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["overwrite"])
async def test_react_overwrite(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with overwrite reactor:
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        
        await tc.async_send_action_event()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_reaction_found()
        # tc.verify_reaction_entity_data()
        
        # await tc.async_verify_reaction_event_received(delay=6)
        # tc.verify_reaction_event_data()
        # tc.verify_trace_record()
        # tc.verify_reaction_not_found()

        await tc.async_stop_all_runs()
        tc.verify_reaction_not_found()
