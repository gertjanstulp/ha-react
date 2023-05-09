from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_available_test"])
async def test_binary_sensor_available(test_context: TstContext, workflow_name: str):
    """
    Test for workflow for binary_sensor availability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await vc.async_set_available("binary_sensor", "binary_sensor_available_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_unavailable_test"])
async def test_binary_sensor_unavailable(test_context: TstContext, workflow_name: str):
    """
    Test for workflow for binary_sensor unavailability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await test_context.async_start_binary_sensor()
    vc = await test_context.async_start_virtual()
    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await vc.async_set_unavailable("binary_sensor", "binary_sensor_unavailable_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()