import pytest

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_DATA,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from tests._plugins.notify_plugin_mock import NOTIFY_PROVIDER_MOCK

from tests.common import (
    FIXTURE_WORKFLOW_NAME,
    TEST_CONTEXT
)
from tests.const import ATTR_NOTIFY_PROVIDER, ATTR_SERVICE_NAME
from tests.tst_context import TstContext


def get_mock_plugin(
    notify_provider: str = None,
    notify_service: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.notify_plugin_mock", 
        ATTR_CONFIG : {
        }
    }

    if notify_provider:
        result[ATTR_CONFIG][ATTR_NOTIFY_PROVIDER] = notify_provider
    if notify_service:
        result[ATTR_CONFIG][ATTR_SERVICE_NAME] = notify_service

    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_service(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_log_warning(f"Notify plugin: Api - {NOTIFY_DOMAIN}.{entity_id} not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_notify_provider(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        # notify_provider=NOTIFY_PROVIDER_MOCK,
        notify_service=entity_id,
    )
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_trace_record()
        tc.verify_has_log_error(f"Notify plugin: Api - Notify provider for '{entity_id}' not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
        notify_service=entity_id,
    )
    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]
    
    plugin_data = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_EVENT_FEEDBACK_ITEMS: "Approve|approve|approved,Deny|deny|denied"
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
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(plugin_data)
        

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_no_notify_provider(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_service=entity_id,
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]


    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_has_log_error(f"Notify plugin: Api - Notify provider not found")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback(hass: HomeAssistant, workflow_name, react_component):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
        notify_service=entity_id,
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    expected_data = {'feedback': ''}
    feedback_data = {
        ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
        ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
        ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text",
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement"
    }

    tc = TstContext(hass, workflow_name)
    react.hass.data[TEST_CONTEXT] = tc
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(data=data_in)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_trace_record(expected_runtime_actor_data=data_in, expected_runtime_reactor_data=[expected_data, data_in])
        tc.verify_has_no_log_issues()
        tc.verify_plugin_data_sent()
        tc.verify_plugin_data_content(feedback_data)
