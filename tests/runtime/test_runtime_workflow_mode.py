import pytest

from datetime import timedelta
from freezegun import freeze_time

from homeassistant.util import dt as dt_util

from custom_components.react.runtime.runtime import WorkflowRuntime

from tests.common import FIXTURE_WORKFLOW_NAME, async_fire_time_changed
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_single"])
async def test_runtime_workflow_mode_abort(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    runtime = test_context.react.runtime.get_workflow_runtime(test_context.workflow_id)
    try:
        await test_context.async_send_action_event()
        assert_run_count(runtime, 1)
        await runtime.async_stop_all_runs()
        assert_run_count(runtime, 0)
    finally:
        await runtime.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_single"])
async def test_runtime_workflow_mode_single(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    runtime = test_context.react.runtime.get_workflow_runtime(test_context.workflow_id)
    try:
        await test_context.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run1 = test_context.react.runtime.run_registry.get_runs(test_context.workflow_id)[-1]
        await test_context.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run2 = test_context.react.runtime.run_registry.get_runs(test_context.workflow_id)[-1]
        assert top_run1.id == top_run2.id, "Expected first job to remain, but got replaced"
    finally:
        await runtime.async_stop_all_runs()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_restart"])
async def test_runtime_workflow_mode_restart(test_context: TstContext, workflow_name: str):
    await test_context.async_start_react()
    runtime = test_context.react.runtime.get_workflow_runtime(test_context.workflow_id)
    try:
        await test_context.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run1 = test_context.react.runtime.run_registry.get_runs(test_context.workflow_id)[-1]
        await test_context.async_send_action_event()
        assert_run_count(runtime, 1)
        top_run2 = test_context.react.runtime.run_registry.get_runs(test_context.workflow_id)[-1]
        assert top_run1.id != top_run2.id, "Expected second job to replace first, but first was found"
    finally:
        await runtime.async_stop_all_runs()
 

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_queued"])
async def test_runtime_workflow_mode_queued(test_context: TstContext, workflow_name: str):
    
    now = dt_util.now()
    with freeze_time(now):
        await test_context.async_start_react()
        runtime = test_context.react.runtime.get_workflow_runtime(test_context.workflow_id)
        try:
            async with test_context.async_listen_reaction_event():
                await test_context.async_send_action_event()
                assert_run_count(runtime, 1)
                await test_context.async_send_action_event()
                assert_run_count(runtime, 2)
                test_context.verify_reaction_event_count(0)
                async_fire_time_changed(test_context.hass, now + timedelta(seconds=4))
                await test_context.hass.async_block_till_done()
                assert_run_count(runtime, 1)
                test_context.verify_reaction_event_count(1)
                async_fire_time_changed(test_context.hass, now + timedelta(seconds=4))
                await test_context.hass.async_block_till_done()
                assert_run_count(runtime, 0)
                test_context.verify_reaction_event_count(2)
        finally:
            await runtime.async_stop_all_runs()
    

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["delayed_long_parallel"])
async def test_runtime_workflow_mode_parallel(test_context: TstContext, workflow_name: str):
    now = dt_util.now()
    with freeze_time(now):
        await test_context.async_start_react()
        runtime = test_context.react.runtime.get_workflow_runtime(test_context.workflow_id)
        async with test_context.async_listen_reaction_event():
            await test_context.async_send_action_event()
            assert_run_count(runtime, 1)
            await test_context.async_send_action_event()
            assert_run_count(runtime, 2)
            test_context.verify_reaction_event_count(0)
            async_fire_time_changed(test_context.hass, now + timedelta(seconds=4))
            await test_context.hass.async_block_till_done()
            assert_run_count(runtime, 0)
            test_context.verify_reaction_event_count(2)


def assert_run_count(runtime: WorkflowRuntime, expected_count: int):
    got_count = runtime.runs
    assert got_count == expected_count, f"Expected job count {expected_count}, got {got_count}"