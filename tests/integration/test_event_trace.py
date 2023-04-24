import pytest
from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace_basic_test"])
async def test_trace_basic_switched_off_actor_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_off("trace_basic_test")
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(reactor_index=1)
        test_context.verify_trace_record(
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace_basic_test"])
async def test_trace_basic_switched_on_actor_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned on:
    - No reaction entity should be created
    - No events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_on("trace_basic_test")

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_trace_record(
            expected_actor_condition_result=False
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace_basic_test"])
async def test_trace_basic_switched_off_actor_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_off("trace_basic_test")
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(actor_index=1)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(reactor_index=1)
        test_context.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace_basic_test"])
async def test_trace_basic_switched_on_actor_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned on:
    - No reaction entity should be created
    - 2 events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_on("trace_basic_test")

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(actor_index=1)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received(expected_count=2)
        test_context.verify_reaction_event_data(event_index=0, reactor_index=0)
        test_context.verify_reaction_event_data(event_index=1, reactor_index=1)
        test_context.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[True, True]
        )

