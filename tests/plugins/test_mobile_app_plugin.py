import pytest

from homeassistant.const import (
    ATTR_DEVICE_ID
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_PLUGIN_PAYLOAD,
    ATTR_PLUGIN_MODULE,
    ATTR_TYPE,
    DOMAIN,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.plugin.mobile_app.const import ATTR_MESSAGE, ATTR_TAG, EVENT_MOBILE_APP_CALLBACK

from tests.tst_context import TstContext
from tests.common import TEST_CONTEXT


@pytest.mark.asyncio
async def test_mobile_app_callback_transform_in(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.mobile_app_plugin_mock"}
    comp = await react_component
    await comp.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data[TEST_CONTEXT] = tc

    DEVICE_ID = "device_id"
    FEEDBACK = "feedback"
    TAG = "tag"
    MESSAGE = "message"

    data_in = {
        ATTR_ACTION: FEEDBACK,
        ATTR_DEVICE_ID: DEVICE_ID,
        ATTR_TAG: TAG,
        ATTR_MESSAGE: MESSAGE
    }

    data_out = {
        ATTR_ENTITY: DEVICE_ID,
        ATTR_TYPE: REACT_TYPE_NOTIFY,
        ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
        ATTR_DATA: {
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: FEEDBACK,
            ATTR_EVENT_PLUGIN_PAYLOAD: {
                ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: TAG,
                ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: DEVICE_ID,
                ATTR_EVENT_FEEDBACK_ITEM_TEXT: MESSAGE,
            }
        }
    }

    async with tc.async_listen_action_event():
        await tc.async_send_event(EVENT_MOBILE_APP_CALLBACK, data_in)
        await tc.async_verify_action_event_received()
        tc.verify_action_event_data(expected_data=data_out)
