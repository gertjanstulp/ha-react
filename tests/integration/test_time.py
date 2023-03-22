from datetime import datetime, timedelta
import pytest, os, time

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.react.const import ATTR_ACTION, ATTR_ID, ATTR_WORKFLOW_WHEN

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_clock"])
async def test_time_clock(hass: HomeAssistant, workflow_name, react_component):
    def set_time(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            action_time = dt_util.now() + timedelta(seconds=5)
            time_pattern = action_time.strftime("%H:%M:%S")
            actor[ATTR_ACTION] = time_pattern
        pass

    comp = await react_component
    await comp.async_setup(workflow_name, process_workflow=set_time)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        await tc.async_verify_reaction_event_received(delay=10)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_pattern"])
async def test_time_pattern(hass: HomeAssistant, workflow_name, react_component):
    def set_time_pattern(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            actor[ATTR_ACTION] = "5s"
        pass

    comp = await react_component
    await comp.async_setup(workflow_name, process_workflow=set_time_pattern)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        await tc.async_verify_reaction_event_received(delay=7, at_least_count=True)
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
