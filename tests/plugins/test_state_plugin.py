from datetime import datetime
import pytest

from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED,
)
from homeassistant.core import State
from homeassistant.util import dt as dt_util

from custom_components.react.const import (
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_PLUGIN_MODULE,
    ATTR_TIMESTAMP,
    REACT_ACTION_CHANGE,
    REACT_TYPE_STATE
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.state.const import ATTR_STATE_PROVIDER
from custom_components.react.plugin.state.setup import WARN_MESSAGE

from tests._plugins.state_mock.setup import STATE_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    state_entity_id: str = None,
    state_entity_state: str = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if state_entity_id:
        result[ATTR_ENTITY_ID] = state_entity_id
    if state_entity_state != None:
        result[ATTR_ENTITY_STATE] = state_entity_state


def get_mock_plugin(
    state_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.state_mock",
        ATTR_CONFIG: {} 
    }
    if state_provider:
        result[ATTR_CONFIG][ATTR_STATE_PROVIDER] = state_provider

    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["state_track_test"])
async def test_state_plugin_api_invalid_provider(test_context: TstContext, workflow_name: str):
    entity_id = "test_domain.state_track_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        state_entity_id=entity_id,
        state_entity_state="test"
    )
    
    data = {
        ATTR_STATE_PROVIDER: invalid_provider
    }
    
    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(entity=entity_id, data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"State plugin: Api - State provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["state_track_test"])
async def test_state_plugin_api_track_state_change_config_provider(test_context: TstContext, workflow_name: str):    
    entity_id = f"test_domain.state_track_test"
    mock_plugin = get_mock_plugin(
        state_provider=STATE_MOCK_PROVIDER,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        state_entity_id=entity_id,
        state_entity_state="asdf",
    )
    await test_context.async_start_react([mock_plugin])

    old_state = "old_state"
    new_state = "new_state"
    timestamp = datetime.now()
    data_in = {
        ATTR_OLD_STATE: old_state,
        ATTR_NEW_STATE: new_state,
        ATTR_TIMESTAMP: timestamp,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_OLD_STATE: old_state,
        ATTR_NEW_STATE: new_state,
        ATTR_TIMESTAMP: timestamp,
    }

    await test_context.async_send_reaction_event(entity=entity_id, data=data_in)
    test_context.verify_has_log_warning(WARN_MESSAGE)
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["state_track_test"])
async def test_state_plugin_api_track_state_change_event_provider(test_context: TstContext, workflow_name: str):    
    entity_id = f"test_domain.state_track_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        state_entity_id=entity_id,
        state_entity_state="asdf",
    )
    await test_context.async_start_react([mock_plugin])

    old_state = "old_state"
    new_state = "new_state"
    timestamp = datetime.now()
    data_in = {
        ATTR_OLD_STATE: old_state,
        ATTR_NEW_STATE: new_state,
        ATTR_TIMESTAMP: timestamp,
        ATTR_STATE_PROVIDER: STATE_MOCK_PROVIDER,
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_OLD_STATE: old_state,
        ATTR_NEW_STATE: new_state,
        ATTR_TIMESTAMP: timestamp,
    }

    await test_context.async_send_reaction_event(entity=entity_id, data=data_in)
    test_context.verify_has_log_warning(WARN_MESSAGE)
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["state_track_test"])
async def test_state_plugin_provider_track_state_change(test_context: TstContext, workflow_name: str):
    entity_id = "input_number.input_number_value_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        state_entity_id=entity_id,
        state_entity_state="asdf",
    )
    await test_context.async_start_react([mock_plugin])

    old_state = "old_state"
    new_state = "new_state"
    timestamp = datetime.now(tz=dt_util.DEFAULT_TIME_ZONE)
    data_in = {
        ATTR_OLD_STATE: old_state,
        ATTR_NEW_STATE: new_state,
        ATTR_TIMESTAMP: timestamp,
    }

    await test_context.async_send_reaction_event(entity=entity_id, data=data_in)
    test_context.verify_has_log_warning(WARN_MESSAGE)
    test_context.verify_has_log_info(f"{timestamp.astimezone(dt_util.DEFAULT_TIME_ZONE)}|{entity_id}|{old_state}|{new_state}")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["state_track_test"])
async def test_state_plugin_input_block_state_change(test_context: TstContext):
    test_entity_id = "input_number.input_number_value_test"
    test_state_old = "test_state_old"
    test_state_new = "test_state_new"
    
    mock_plugin = mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])

    last_changed = datetime.now()
    data_in = {
        ATTR_ENTITY_ID: test_entity_id,
        ATTR_OLD_STATE: State(test_entity_id, test_state_old, last_changed=last_changed),
        ATTR_NEW_STATE: State(test_entity_id, test_state_new, last_changed=last_changed),
    }
    expected_data = {
        ATTR_OLD_STATE: test_state_old,
        ATTR_NEW_STATE: test_state_new,
        ATTR_TIMESTAMP: last_changed,
    }

    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=test_entity_id,
            expected_type=REACT_TYPE_STATE,
            expected_action=REACT_ACTION_CHANGE,
            expected_data=expected_data)
