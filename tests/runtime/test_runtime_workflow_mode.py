from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant
from custom_components.react.base import ReactBase
from custom_components.react.const import DOMAIN
from custom_components.react.runtime.runtime import WorkflowRuntime

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_single"])
async def test_runtime_workflow_mode_abort(hass: HomeAssistant, workflow_name, react_component):

    await react_component.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]
    workflow_id = f"workflow_{workflow_name}"
    runtime = react.runtime.get_workflow_runtime(workflow_id)
    
    try:
        tc = TstContext(hass, workflow_name)
        await tc.async_send_action_event()

        assert_run_count(runtime, 1)
        await runtime.async_stop_all_runs()
        assert_run_count(runtime, 0)
    finally:
        await runtime.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_single"])
async def test_runtime_workflow_mode_single(hass: HomeAssistant, workflow_name, react_component):
    
    await react_component.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]
    workflow_id = f"workflow_{workflow_name}"
    runtime = react.runtime.get_workflow_runtime(workflow_id)
    

    try:
        tc = TstContext(hass, workflow_name)
        await tc.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run1 = react.runtime.run_registry.get_runs(workflow_id)[-1]
        await tc.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run2 = react.runtime.run_registry.get_runs(workflow_id)[-1]
        assert top_run1.id == top_run2.id, "Expected first job to remain, but got replaced"
    finally:
        await runtime.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_restart"])
async def test_runtime_workflow_mode_restart(hass: HomeAssistant, workflow_name, react_component):
    
    await react_component.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]
    workflow_id = f"workflow_{workflow_name}"
    runtime = react.runtime.get_workflow_runtime(workflow_id)

    try:
        tc = TstContext(hass, workflow_name)
        await tc.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run1 = react.runtime.run_registry.get_runs(workflow_id)[-1]
        await tc.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run2 = react.runtime.run_registry.get_runs(workflow_id)[-1]
        assert top_run1.id != top_run2.id, "Expected second job to replace first, but first was found"
    finally:
        await runtime.async_stop_all_runs()
 

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_queued"])
async def test_runtime_workflow_mode_queued(hass: HomeAssistant, workflow_name, react_component):
    
    await react_component.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]
    workflow_id = f"workflow_{workflow_name}"
    runtime = react.runtime.get_workflow_runtime(workflow_id)

    try:
        tc = TstContext(hass, workflow_name)
        async with tc.async_listen_reaction_event():
            await tc.async_send_action_event()
            assert_run_count(runtime, 1)
            await tc.async_send_action_event()
            assert_run_count(runtime, 2)
            tc.verify_reaction_event_count(0)
            await sleep(4)
            assert_run_count(runtime, 1)
            tc.verify_reaction_event_count(1)
            await sleep(4)
            assert_run_count(runtime, 0)
            tc.verify_reaction_event_count(2)
    finally:
        await runtime.async_stop_all_runs()
    


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_parallel"])
async def test_runtime_workflow_mode_parallel(hass: HomeAssistant, workflow_name, react_component):
    
    await react_component.async_setup(workflow_name)

    react: ReactBase = hass.data[DOMAIN]
    workflow_id = f"workflow_{workflow_name}"
    runtime = react.runtime.get_workflow_runtime(workflow_id)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        await tc.async_send_action_event()
        assert_run_count(runtime, 1)
        await tc.async_send_action_event()
        assert_run_count(runtime, 2)
        tc.verify_reaction_event_count(0)
        await sleep(4)
        assert_run_count(runtime, 0)
        tc.verify_reaction_event_count(2)


def assert_run_count(runtime: WorkflowRuntime, expected_count: int):
    got_count = runtime.runs
    assert got_count == expected_count, f"Expected job count {expected_count}, got {got_count}"