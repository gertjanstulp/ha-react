import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor"])
async def test_multiple_actor_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with multiple actors using first actor:
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor"])
async def test_multiple_actor_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with multiple actors using second actor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(actor_index=1)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record(actor_index=1)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_reactor"])
async def test_multiple_reactor(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with multiple reactors:
    - No reaction entities should be created
    - An event should be sent for each reactor (2)
    - Event data should match configuration for each reactor (2)
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_reaction_event_data(event_with_reactor_id="0", reactor_index=0)
        test_context.verify_reaction_event_data(event_index=1, reactor_index=1)
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_entities"])
async def test_multiple_entities_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with an actor containing multiple entities
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
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_reaction_event_data(event_with_entity_name="reactor_entity_multiple_entities_1")
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_entities"])
async def test_multiple_entities_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with an actor containing multiple entities
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(entity_index=1)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        # test_context.verify_reaction_event_data()
        test_context.verify_reaction_event_data(entity_index=1, event_with_entity_name="reactor_entity_multiple_entities_2")
        test_context.verify_trace_record(actor_entity_index=1)
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["entity_groups_test"])
async def test_entity_groups(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=3)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actions_test"])
async def test_multiple_actions_1(test_context: TstContext, workflow_name: str):
    
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_reaction_event_data(event_with_action_name="reactor_action_multiple_actions_1")
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actions_test"])
async def test_multiple_actions_2(test_context: TstContext, workflow_name: str):
  
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(action_index=1)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_reaction_event_data(event_with_action_name="reactor_action_multiple_actions_1")
        test_context.verify_trace_record(actor_action_index=1)
        test_context.verify_has_no_log_issues()