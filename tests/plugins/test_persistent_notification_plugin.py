import pytest

from homeassistant.components.notify.const import (
    ATTR_MESSAGE,
)
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN,
    ATTR_NOTIFICATION_ID,
)
from homeassistant.const import (
    ATTR_DOMAIN,
    EVENT_STATE_CHANGED
)

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    DOMAIN,
    REACT_ACTION_DISMISSED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.persistent_notification.const import (
    ATTR_NEW_STATE, 
    ATTR_OBJECT_ID, 
    ATTR_OLD_STATE, 
    SERVICE_CREATE
)

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import ATTR_SERVICE_NAME, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    notify_entity_id: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id


def get_mock_plugin():
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.persistent_notification_mock", 
        ATTR_CONFIG: {}
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_persistent_notification_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_entity_id=entity_id
    )

    await test_context.async_start_react(mock_plugin)
    
    data = {
        ATTR_MESSAGE: "Approve something",
        ATTR_NOTIFICATION_ID: entity_id
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_service_call_sent()
        test_context.verify_service_call_content(PERSISTENT_NOTIFICATION_DOMAIN, SERVICE_CREATE, data)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_persistent_notification_task_dismiss_transform_in(test_context: TstContext):
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react(mock_plugin)
    
    test_id = "test_id"
    data_in = {
        ATTR_OLD_STATE : {
            ATTR_DOMAIN: PERSISTENT_NOTIFICATION_DOMAIN,
            ATTR_OBJECT_ID: test_id
        },
        ATTR_NEW_STATE : None
    }
    data_out = {
        ATTR_ENTITY: PERSISTENT_NOTIFICATION_DOMAIN,
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_DISMISSED,
        ATTR_DATA: {
            ATTR_OBJECT_ID: test_id
        }
    }


    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(expected_data=data_out)
