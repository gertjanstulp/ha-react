import pytest

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
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
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
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
from custom_components.react.plugin.persistent_notification.const import ATTR_NEW_STATE, ATTR_OBJECT_ID, ATTR_OLD_STATE, SERVICE_CREATE
from tests.const import ATTR_SERVICE_NAME

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT


def get_mock_plugin(
    notify_entity_id: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.persistent_notification_plugin_mock", 
        ATTR_CONFIG: {}
    }
    if notify_entity_id:
        result[ATTR_CONFIG][ATTR_SERVICE_NAME] = notify_entity_id
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_persistent_notification_plugin_provider_notify_send_message(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_entity_id=entity_id
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data = {
        ATTR_MESSAGE: "Approve something",
        ATTR_NOTIFICATION_ID: entity_id
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_no_log_issues()
        tc.verify_service_call_sent()
        tc.verify_service_call_content(PERSISTENT_NOTIFICATION_DOMAIN, SERVICE_CREATE, data)


@pytest.mark.asyncio
async def test_persistent_notification_task_dismiss_transform_in(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.persistent_notification_plugin_mock"}
    comp = await react_component
    await comp.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data[TEST_CONTEXT] = tc

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


    async with tc.async_listen_action_event():
        await tc.async_send_event(EVENT_STATE_CHANGED, data_in)
        await tc.async_verify_action_event_received()
        tc.verify_action_event_data(expected_data=data_out)
