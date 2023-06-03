from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

FIXTURE_ADDITIONAL_TESTS = "additional_tests"

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["immediate"])
async def test_immediate(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with immediate reactor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()



@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed"])
async def test_delayed(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with delayed reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - An event should be sent after a configured delay
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        await test_context.async_verify_reaction_event_received(delay=6)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_reaction_not_found()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled"])
async def test_scheduled(test_context: TstContext, workflow_name: str):
    """ 
    Test for workflow with scheduled reactor:
    - An event should not be sent immediately
    - A reaction entity should be created
    - Reaction entity data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        test_context.verify_trace_record(expected_event_trace=False)
        await test_context.async_stop_all_runs()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reset"])
async def test_reset(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with reset reactor:
    - Reactions should be found before sending reset event
    - No reactions should be found after sending reset event
    - Trace data should match configuration
    """
    
    await test_context.async_start_react(additional_workflows=["delayed", "scheduled"])

    tc_delayed = await TstContext(test_context.hass, test_context.react_component, "delayed").async_start_react(skip_setup=True)
    tc_scheduled = await TstContext(test_context.hass, test_context.react_component, "scheduled").async_start_react(skip_setup=True)

    async with tc_delayed.async_listen_reaction_event():
        await tc_delayed.async_send_action_event()
    async with tc_scheduled.async_listen_reaction_event():
        await tc_scheduled.async_send_action_event()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_found(2)
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        test_context.verify_trace_record()

    await tc_delayed.async_stop_all_runs()
    await tc_scheduled.async_stop_all_runs()
    
    test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_action"])
async def test_forward_action_no_toggle(test_context: TstContext, workflow_name: str):
    """ 
    Test for workflow with reactor with forwardaction and not event action 'toggle':
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration and forwarded action
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(action="test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_action="test")
        test_context.verify_trace_record(expected_runtime_actor_action="test")
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_action"])
async def test_forward_action_toggle(test_context: TstContext, workflow_name: str):
    """ 
    Test for workflow with reactor with forwardaction and event action 'toggle':
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(action="toggle")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_trace_record(expected_result_message="Skipped, toggle with forward-action")
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["forward_data"])
async def test_forward_data(test_context: TstContext, workflow_name: str):
    """ 
    Test for workflow with reactor with forwarddata :
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration and forwarded data
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    data_in: dict = {
        "data1" : 37,
        "data2": ["asdf", "qwer"],
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_data=data_in)
        test_context.verify_trace_record(expected_runtime_reactor_data=[data_in])
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["full_stencil"])
async def test_full_stencil(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with full stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    data_out: dict = {
        "test": 37
    }
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_data=data_out)
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["partial_stencil"])
async def test_partial_stencil(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with partial stencil:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["overwrite"])
async def test_overwrite(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with overwrite reactor:
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        
        # await test_context.async_verify_reaction_event_received(delay=6)
        # test_context.verify_reaction_event_data()
        # test_context.verify_trace_record()
        # test_context.verify_reaction_not_found()

        await test_context.async_stop_all_runs()
        test_context.verify_reaction_not_found()
        test_context.verify_has_no_log_issues()
