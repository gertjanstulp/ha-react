import pytest

from homeassistant.components.notify.const import (
    ATTR_MESSAGE,
)
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN,
    ATTR_NOTIFICATION_ID,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED
)
from homeassistant.core import State

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    REACT_ACTION_DISMISSED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.const import (
    ATTR_CONFIG, 
    ATTR_OBJECT_ID,
)
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER 
from custom_components.react.plugin.persistent_notification.const import (
    NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION,
    SERVICE_CREATE
)
from tests._mocks import mock_data

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.const import ATTR_SERVICE_NAME, ATTR_SETUP_MOCK_PROVIDER, TEST_CONFIG
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_notify_provider: bool = False,
    notify_entity_id: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_notify_provider
    }
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id


def get_mock_plugins():
    result = [
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.notify_mock",
            ATTR_CONFIG: {
                ATTR_NOTIFY_PROVIDER: NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION
            }
        },
        {
            ATTR_PLUGIN_MODULE: "tests._plugins.persistent_notification_mock", 
            ATTR_CONFIG: {}
        }
    ]
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_persistent_notification_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
        notify_entity_id=entity_id
    )

    await test_context.async_start_react(mock_plugins)
    
    data_out = {
        ATTR_MESSAGE: mock_data.TEST_NOTIFY_EVENT_MESSAGE,
        ATTR_NOTIFICATION_ID: entity_id
    }

    await test_context.async_send_reaction_event(data=mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_IN)
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(PERSISTENT_NOTIFICATION_DOMAIN, SERVICE_CREATE, data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, [""])
async def test_persistent_notification_task_notification_dismissed_action(test_context: TstContext):
    mock_plugins = get_mock_plugins()
    set_test_config(test_context,
        setup_mock_notify_provider=True,
    )

    await test_context.async_start_react(mock_plugins)
    
    test_id = "test_id"
    data_in = {
        ATTR_ENTITY_ID: F"{PERSISTENT_NOTIFICATION_DOMAIN}.{test_id}",
        ATTR_OLD_STATE: State(f"{PERSISTENT_NOTIFICATION_DOMAIN}.{test_id}", None),
        ATTR_NEW_STATE : None
    }
    expected_data = {
        ATTR_OBJECT_ID: test_id
    }


    async with test_context.async_listen_action_event():
        await test_context.async_send_event(EVENT_STATE_CHANGED, data_in)
        await test_context.async_verify_action_event_received()
        test_context.verify_action_event_data(
            expected_entity=PERSISTENT_NOTIFICATION_DOMAIN,
            expected_type=REACT_TYPE_NOTIFY,
            expected_action=REACT_ACTION_DISMISSED,
            expected_data=expected_data
        )
