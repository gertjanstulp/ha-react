import pytest

from astral import LocationInfo, sun

from datetime import datetime, timedelta
from freezegun import freeze_time

from homeassistant.const import (
    SUN_EVENT_SUNRISE,
    SUN_EVENT_SUNSET,
)
from homeassistant.util import dt as dt_util

from custom_components.react.const import (
    ACTOR_ENTITY_CLOCK,
    ACTOR_ENTITY_PATTERN,
    ACTOR_ENTITY_SUN,
    ACTOR_TYPE_TIME,
    ATTR_ACTION, 
    ATTR_PLUGIN_MODULE, 
    ATTR_WORKFLOW_WHEN,
)
from custom_components.react.plugin.const import ATTR_CONFIG

from tests.common import FIXTURE_WORKFLOW_NAME, async_fire_time_changed
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
async def test_time_pattern(test_context: TstContext, workflow_name: str):
    test_pattern = "::/5"
    def set_time_pattern(workflow: dict):
        actor = workflow.get(ATTR_WORKFLOW_WHEN, [])
        if actor:
            actor[ATTR_ACTION] = test_pattern
        pass
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    test_time = dt_util.now().replace(second=5)

    with freeze_time(test_time - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin], process_workflow=set_time_pattern)

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, test_time)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received(expected_count=1)
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_PATTERN,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=test_pattern,
                event_index=0)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_clock"])
async def test_time_clock(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    
    test_time_string = "23:59:59"
    test_time = dt_util.now().replace(hour=23, minute=59, second=59)

    with freeze_time(test_time - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin])

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, test_time)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received()
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_CLOCK,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=test_time.strftime(test_time_string),
                event_index=0)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_sunrise"])
async def test_time_sunrise(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    location = LocationInfo(latitude=test_context.hass.config.latitude, longitude=test_context.hass.config.longitude)
    next_rising = sun.sunrise(location.observer, date=datetime.now())

    with freeze_time(next_rising - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin])

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, next_rising)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received()
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_SUN,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=SUN_EVENT_SUNRISE,
                event_index=0
            )
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_sunrise_with_offset"])
async def test_time_sunrise_with_offset(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    location = LocationInfo(latitude=test_context.hass.config.latitude, longitude=test_context.hass.config.longitude)
    next_rising = sun.sunrise(location.observer, date=datetime.now()) + timedelta(minutes=30)

    with freeze_time(next_rising - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin])

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, next_rising)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received()
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_SUN,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=SUN_EVENT_SUNRISE,
                event_index=0
            )
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_sunset"])
async def test_time_sunset(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    location = LocationInfo(latitude=test_context.hass.config.latitude, longitude=test_context.hass.config.longitude)
    next_rising = sun.sunset(location.observer, date=datetime.now())

    with freeze_time(next_rising - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin])

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, next_rising)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received()
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_SUN,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=SUN_EVENT_SUNSET,
                event_index=0
            )
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["time_sunset_with_offset"])
async def test_time_sunset_with_offset(test_context: TstContext, workflow_name: str):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    location = LocationInfo(latitude=test_context.hass.config.latitude, longitude=test_context.hass.config.longitude)
    next_rising = sun.sunset(location.observer, date=datetime.now()) - timedelta(minutes=30)

    with freeze_time(next_rising - timedelta(seconds=1)):
        await test_context.async_start_react([mock_plugin])

        async with test_context.async_listen_action_event():
            await test_context.async_verify_action_event_not_received()
            async_fire_time_changed(test_context.hass, next_rising)
            await test_context.hass.async_block_till_done()
            await test_context.async_verify_action_event_received()
            test_context.verify_action_event_data(
                expected_entity=ACTOR_ENTITY_SUN,
                expected_type=ACTOR_TYPE_TIME,
                expected_action=SUN_EVENT_SUNSET,
                event_index=0
            )
