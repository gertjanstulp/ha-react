import pytest

from homeassistant.const import ATTR_ENTITY_ID

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE, 
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER

from tests._plugins.group_mock.plugin import (
    ATTR_CHILD_SERVICE, 
    ATTR_KILL_CHILD_PROVIDER, 
    ATTR_KILL_RESOLVER
)
from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
)
from tests.const import (
    ATTR_SERVICE_NAME,
    TEST_CONFIG
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    notify_provider: str = None,
    notify_entity_id: str = None,
    child_service: str = None,
    kill_resolver: bool = False,
    kill_child_provider: bool = False,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {}
    if notify_provider:
        result[ATTR_NOTIFY_PROVIDER] = notify_provider
    if notify_entity_id:
        result[ATTR_SERVICE_NAME] = notify_entity_id
    if child_service:
        result[ATTR_CHILD_SERVICE] = child_service
    if kill_resolver:
        result[ATTR_KILL_RESOLVER] = True
    if kill_child_provider:
        result[ATTR_KILL_CHILD_PROVIDER] = True
    

def get_mock_plugin(
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.group_mock", 
        ATTR_CONFIG: {}
    }
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_resolver(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        kill_resolver=True,
    )

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_log_error("Group plugin: Provider - Notify resolver not found, notify plugin is not configured")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_group_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
    )

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_log_error(f"Group plugin: Provider - Could not find notify platform for entity '{entity_id}'")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_child_provider(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        child_service=child_entity_id,
        kill_child_provider=True,
    )

    await test_context.async_start_react(mock_plugin)
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_log_warning(f"Group plugin: Provider - Could not find notify provider for child entity '{child_entity_id}'")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_send_message(test_context: TstContext, workflow_name: str):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        child_service=child_entity_id
    )

    await test_context.async_start_react(mock_plugin)
    
    plugin_data = {
        ATTR_ENTITY_ID: child_entity_id,
        ATTR_EVENT_MESSAGE: "Approve something",
        ATTR_EVENT_FEEDBACK_ITEMS: "Approve|approve|approved,Deny|deny|denied"
    }

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_trace_record()
        test_context.verify_has_no_log_issues()
        test_context.verify_plugin_data_sent()
        test_context.verify_plugin_data_content(plugin_data)
