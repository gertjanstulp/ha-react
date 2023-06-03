import pytest

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN

from homeassistant.const import (
    ATTR_ENTITY_ID
)

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_FEEDBACK_ITEMS, 
    ATTR_EVENT_MESSAGE,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    ATTR_PLUGIN_MODULE, 
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER
from tests._mocks import mock_data

from tests._plugins.notify_mock.setup import NOTIFY_PROVIDER_MOCK
from tests.common import (
    FIXTURE_WORKFLOW_NAME,
)
from tests.const import (
    ATTR_SERVICE_NAME,
    ATTR_SETUP_MOCK_PROVIDER,
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    notify_service: str = None,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if notify_service:
        result[ATTR_SERVICE_NAME] = notify_service


def get_mock_plugin(
    notify_provider: str = None,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.notify_mock", 
        ATTR_CONFIG : {
        }
    }
    if notify_provider:
        result[ATTR_CONFIG][ATTR_NOTIFY_PROVIDER] = notify_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_service(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_has_log_warning(f"Notify plugin: Api - {NOTIFY_DOMAIN}.{entity_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_provider_provided(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider for '{entity_id}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_no_provider_set_up(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK
    )
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data={})
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider for '{entity_id}/{NOTIFY_PROVIDER_MOCK}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_event_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK
    }
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: mock_data.TEST_NOTIFY_EVENT_MESSAGE,
        ATTR_EVENT_FEEDBACK_ITEMS: mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_OUT_FEEDBACK_ITEMS_STRING
    }

    await test_context.async_send_reaction_event(data=data_in | mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_IN)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_notify_plugin_api_send_message_config_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_out = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_EVENT_MESSAGE: mock_data.TEST_NOTIFY_EVENT_MESSAGE,
        ATTR_EVENT_FEEDBACK_ITEMS: mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_OUT_FEEDBACK_ITEMS_STRING
    }

    await test_context.async_send_reaction_event(data=mock_data.TEST_NOTIFY_SEND_MESSAGE_DATA_IN)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_no_provider_set_up(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])

    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider for '{NOTIFY_PROVIDER_MOCK}' not found")
        

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_no_provider_provided(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])

    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"Notify plugin: Api - Notify provider not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_event_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    data_out = {
        ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
        ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
        ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text",
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement"
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_confirm_feedback_test"])
async def test_notify_plugin_api_confirm_feedback_config_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_MOCK,
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        notify_service=entity_id,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement",
        # ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOCK,
        ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text"
        }
    }
    data_out = {
        ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: "conversation_id",
        ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: "messageid",
        ATTR_EVENT_FEEDBACK_ITEM_TEXT: "text",
        ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: "acknowledgement"
    }

    await test_context.async_send_reaction_event(reactor_index=1, data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)
