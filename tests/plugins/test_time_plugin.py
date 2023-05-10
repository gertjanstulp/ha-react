import pytest
from datetime import timedelta

from homeassistant.util import dt as dt_util

from custom_components.react.const import (
    ACTOR_ENTITY_TIME, 
    ACTOR_TYPE_CLOCK, 
    ACTOR_TYPE_PATTERN, 
    ATTR_ACTION, 
    ATTR_PLUGIN_MODULE, 
    ATTR_WORKFLOW_WHEN,
)
from custom_components.react.plugin.const import ATTR_CONFIG

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
) -> dict:
    test_context.hass.data[TEST_CONFIG] = {}


def get_mock_plugin(
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.time_mock",
        ATTR_CONFIG: {} 
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_pattern"])
async def test_time_five_second_pattern(test_context: TstContext, workflow_name: str):
    def set_time_pattern(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            actor[ATTR_ACTION] = "::/5"
        pass

    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    await test_context.async_start_react([mock_plugin], process_workflow=set_time_pattern)

    async with test_context.async_listen_action_event():
        await test_context.async_verify_action_event_not_received()
        await test_context.async_verify_action_event_received(expected_count=1, delay=5)
        test_context.verify_action_event_data(
            expected_entity=ACTOR_ENTITY_TIME,
            expected_type=ACTOR_TYPE_PATTERN,
            expected_action="::/5",
            event_index=0)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_clock"])
async def test_time_clock(test_context: TstContext, workflow_name: str):
    test_time: str = (dt_util.now() + timedelta(seconds=3)).strftime("%H:%M:%S")
    def set_time(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            actor[ATTR_ACTION] = test_time 
        pass

    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    await test_context.async_start_react([mock_plugin], process_workflow=set_time)

    async with test_context.async_listen_action_event():
        await test_context.async_verify_action_event_not_received()
        await test_context.async_verify_action_event_received(delay=4)
        test_context.verify_action_event_data(
            expected_entity=ACTOR_ENTITY_TIME,
            expected_type=ACTOR_TYPE_CLOCK,
            expected_action=test_time,
            event_index=0)