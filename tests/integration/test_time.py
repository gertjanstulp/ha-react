from datetime import datetime, timedelta
import pytest, os, time

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.react.const import ATTR_ACTION, ATTR_ID, ATTR_WORKFLOW_WHEN

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_clock"])
async def test_time_clock(test_context: TstContext, workflow_name: str):
    def set_time(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            action_time = dt_util.now() + timedelta(seconds=5)
            time_pattern = action_time.strftime("%H:%M:%S")
            actor[ATTR_ACTION] = time_pattern
        pass

    await test_context.async_start_react(process_workflow=set_time)
    # await test_context.react_component.async_setup(workflow_name, process_workflow=set_time)

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        await test_context.async_verify_reaction_event_received(delay=10)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_pattern"])
async def test_time_pattern(test_context: TstContext, workflow_name: str):
    def set_time_pattern(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            actor[ATTR_ACTION] = "5s"
        pass

    await test_context.async_start_react(process_workflow=set_time_pattern)
    # await test_context.react_component.async_setup(workflow_name, process_workflow=set_time_pattern)

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        await test_context.async_verify_reaction_event_received(delay=7, at_least_count=True)
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
