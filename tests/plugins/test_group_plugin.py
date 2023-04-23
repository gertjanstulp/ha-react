import pytest

from homeassistant.components.group import DOMAIN as GROUP_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE, 
    ATTR_PLUGIN_MODULE, 
    DOMAIN
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP

from tests._plugins.group_plugin_mock import (
    ATTR_CHILD_SERVICE, 
    ATTR_KILL_CHILD_PROVIDER, 
    ATTR_KILL_RESOLVER
)
from tests.common import (
    FIXTURE_WORKFLOW_NAME, 
    TEST_CONTEXT
)
from tests.const import (
    ATTR_NOTIFY_PROVIDER, 
    ATTR_SERVICE_NAME
)
from tests.tst_context import TstContext


def get_mock_plugin(
    notify_provider: str = None,
    notify_entity_id: str = None,
    child_service: str = None,
    kill_resolver: bool = False,
    kill_child_provider: bool = False,
):
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.group_plugin_mock", 
        ATTR_CONFIG: {}
    }

    if notify_provider:
        result[ATTR_CONFIG][ATTR_NOTIFY_PROVIDER] = notify_provider
    if notify_entity_id:
        result[ATTR_CONFIG][ATTR_SERVICE_NAME] = notify_entity_id
    if child_service:
        result[ATTR_CONFIG][ATTR_CHILD_SERVICE] = child_service
    if kill_resolver:
        result[ATTR_CONFIG][ATTR_KILL_RESOLVER] = True
    if kill_child_provider:
        result[ATTR_CONFIG][ATTR_KILL_CHILD_PROVIDER] = True
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_resolver(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        kill_resolver=True,
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
        tc.verify_has_log_error("Group plugin: Provider - Notify resolver not found, notify plugin is not configured")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_group_provider(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
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
        tc.verify_has_log_error(f"Group plugin: Provider - Could not find notify platform for entity '{entity_id}'")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_no_child_provider(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        child_service=child_entity_id,
        kill_child_provider=True,
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
        tc.verify_has_log_warning(f"Group plugin: Provider - Could not find notify provider for child entity '{child_entity_id}'")


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["notify_send_message_test"])
async def test_group_plugin_provider_notify_send_message(hass: HomeAssistant, react_component, workflow_name):
    entity_id = "mobile_group"
    child_entity_id = "mobile_item"
    mock_plugin = get_mock_plugin(
        notify_provider=NOTIFY_PROVIDER_GROUP,
        notify_entity_id=entity_id,
        child_service=child_entity_id
    )

    comp = await react_component
    await comp.async_setup(workflow_name, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    plugin_data = {
        ATTR_ENTITY_ID: child_entity_id,
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