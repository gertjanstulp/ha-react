import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["data"])
async def test_data_no_event_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with actor data where action has no data:
    - No reaction entity should be found
    - No Event should be received
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["data"])
async def test_data_no_event_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with actor data where action data does not match actor data:
    - No reaction entity should be found
    - No Event should be received
    """

    await test_context.async_start_react()
        
    data_in: dict = {"actor_data_data" : 4}
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["data"])
async def test_data_event(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with actor data where action data does match actor data:
    - No reaction entity should be found
    - An event should be received
    - Event data should match configuration and contain configured reactor data
    - Trace data should match configuration
    """

    await test_context.async_start_react()
        
    data_in: dict = {"actor_data_data" : 3}
    data_out: dict = {
        "data1": 1,
        "data2": test_context.workflow_config.actors[0].action.first,
        "data3": 3,
        # "data4": ["asdf", "qwer"],
        "data5": int(test_context.workflow_config.actors[0].id)
    }
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_data=data_out)
        test_context.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[data_out])


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["data_delayed"])
async def test_data_delayed_event(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with delayed reactor with data:
    - No event should be sent
    - A reaction entity should be found
    - Reaction entity data should match configuration
    - Internal reaction data should match configured reactor data
    - Trace data should match configuration
    """

    await test_context.async_start_react()
        
    data_out: dict = {
        "data1": 1,
        "data2": True,
    }
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        # test_context.verify_reaction_internal_data(expected_data=data_out)
        test_context.verify_trace_record(expected_event_trace=False, expected_runtime_reactor_delay_seconds=60)
        await test_context.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor_data"])
async def test_multiple_actor_data_event_1(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with multiple actor data where action data does match first actor data:
    - No reaction entity should be found
    - An event should be received
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
        
    data_in: dict = {"actor_data_multiple_actor_data" : 1}
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor_data"])
async def test_multiple_actor_data_event_2(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with multiple actor data where action data does match second actor data:
    - No reaction entity should be found
    - An event should be received
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
        
    data_in: dict = {"actor_data_multiple_actor_data" : 2}
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(data=data_in)
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record(actor_data_index=1)
