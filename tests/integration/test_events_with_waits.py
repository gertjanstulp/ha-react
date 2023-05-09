import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_test"])
async def test_wait_for_state_initial_false(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with wait reactor:
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        await ibc.async_turn_on("wait_for_state_test")
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_delayed_test"])
async def test_wait_for_state_delayed_initial_false(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with delayed wait reactor:
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        await ibc.async_turn_on("wait_for_state_delayed_test")
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        await test_context.async_verify_reaction_event_received(delay=6)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_reaction_not_found()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["wait_for_state_delayed_test"])
async def test_wait_for_state_delayed_initial_true(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with delayed wait reactor
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()

    async with test_context.async_listen_reaction_event():
        await ibc.async_turn_on("wait_for_state_delayed_test")
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_reaction_found()
        # test_context.verify_reaction_entity_data()
        await test_context.async_verify_reaction_event_received(delay=6)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
        test_context.verify_reaction_not_found()
