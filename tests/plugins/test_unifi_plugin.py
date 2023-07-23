from typing import Any
import pytest

from homeassistant.components.unifi.const import DOMAIN
from homeassistant.components.unifi.services import SERVICE_RECONNECT_CLIENT
from homeassistant.const import ATTR_DEVICE_ID

from custom_components.react.const import ATTR_PLUGIN_MODULE
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.unifi.const import ATTR_UNIFI_PROVIDER

from tests._plugins.unifi_mock.setup import UNIFI_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME, VALUE_FIXTURE_COMBOS, VALUE_FIXTURES
from tests.const import (
    ATTR_DEVICE_DISABLED,
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
    device_id: str = None,
    device_disabled: bool = None
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }
    if device_id:
        result[ATTR_DEVICE_ID] = device_id
    if device_disabled != None:
        result[ATTR_DEVICE_DISABLED] = device_disabled


def get_mock_plugin(
    unifi_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.unifi_mock",
        ATTR_CONFIG: {} 
    }
    if unifi_provider:
        result[ATTR_CONFIG][ATTR_UNIFI_PROVIDER] = unifi_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["unifi_reconnect_client_test"])
async def test_unifi_plugin_api_reconnect_client_invalid_device(test_context: TstContext, workflow_name: str):
    device_id = "device_id_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - Device with device_id {device_id} not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["unifi_reconnect_client_test"])
async def test_unifi_plugin_api_reconnect_client_disabled_device(test_context: TstContext, workflow_name: str):
    device_id = "device_id_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        device_id=device_id,
        device_disabled=True
    )

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event()
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_warning(f"1 - Device with device_id {device_id} is disabled")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["unifi_reconnect_client_test"])
async def test_unifi_plugin_api_reconnect_client_invalid_provider(test_context: TstContext, workflow_name: str):
    device_id = "device_id_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        device_id=device_id,
    )
    
    data = {
        ATTR_UNIFI_PROVIDER: invalid_provider,
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Unifi provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["unifi_reconnect_client_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_unifi_plugin_api_reconnect_client(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):
    device_id = "device_id_test"
    mock_plugin = get_mock_plugin(
        unifi_provider=UNIFI_MOCK_PROVIDER if config_value else None
    )
    set_test_config(test_context,
        setup_mock_provider=True,
        device_id=device_id,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_UNIFI_PROVIDER: UNIFI_MOCK_PROVIDER if event_value else None,
    }
    data_out = {
        ATTR_DEVICE_ID: device_id,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["unifi_reconnect_client_test"])
async def test_unifi_plugin_generic_provider_reconnect_client(test_context: TstContext, workflow_name: str):
    device_id = "device_id_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context,
        device_id=device_id,
    )

    await test_context.async_start_react([mock_plugin])

    data_out = {
        ATTR_DEVICE_ID: device_id,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(DOMAIN, SERVICE_RECONNECT_CLIENT, data_out)
