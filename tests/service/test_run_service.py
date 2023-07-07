import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_some_days"])
async def test_call_service_delete_run(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    async with test_context.async_listen_reaction_event():
        test_context.verify_run_not_found()
        await test_context.async_send_action_event()
        test_context.verify_run_found()
        run_id = test_context.retrieve_run_id()
        await test_context.react_component.async_call_service_delete_run(run_id)
        await test_context.hass.async_block_till_done()
        test_context.verify_run_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace_advanced_test"])
async def test_call_service_delete_run_multiple_reactions(test_context: TstContext, workflow_name: str):
    
    ibc = await test_context.async_start_input_boolean()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_run_not_found()
        await ibc.async_turn_on("trace_advanced_test")
        await test_context.async_send_action_event(entity="actor_entity_trace_advanced_test_2", type="actor_type_trace_advanced_test_2", action="actor_action_trace_advanced_test_2")
        test_context.verify_run_found()
        test_context.verify_reaction_found(expected_count=2)
        run_id = test_context.retrieve_run_id()
        await test_context.react_component.async_call_service_delete_run(run_id)
        await test_context.hass.async_block_till_done()
        test_context.verify_run_not_found()
        test_context.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["scheduled_some_days"])
async def test_call_service_run_now(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    async with test_context.async_listen_reaction_event():
        test_context.verify_run_not_found()
        await test_context.async_send_action_event()
        test_context.verify_run_found()
        run_id = test_context.retrieve_run_id()
        await test_context.react_component.async_call_service_run_now(run_id)
        await test_context.hass.async_block_till_done()
        test_context.verify_run_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()