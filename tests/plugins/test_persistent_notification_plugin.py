import pytest

from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN, 
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
from custom_components.react.plugin.persistent_notification.const import ATTR_NEW_STATE, ATTR_OBJECT_ID, ATTR_OLD_STATE

from tests.tst_context import TstContext
from tests.common import TEST_CONTEXT


@pytest.mark.asyncio
async def test_persistent_notification_dismiss_transform_in(hass: HomeAssistant, react_component):
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
