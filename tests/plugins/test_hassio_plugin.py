from typing import Any
import pytest

from homeassistant.components.hassio import SERVICE_ADDON_RESTART
from homeassistant.components.hassio.const import DOMAIN, ATTR_ADDON
from homeassistant.const import ATTR_DEVICE_ID

from custom_components.react.const import (
    ACTION_CHANGE,
    ATTR_PLUGIN_MODULE,
)
from custom_components.react.plugin.const import ATTR_CONFIG
from custom_components.react.plugin.hassio.const import ATTR_HASSIO_PROVIDER

from tests._plugins.hassio_mock.setup import HASSIO_MOCK_PROVIDER
from tests.common import FIXTURE_WORKFLOW_NAME, VALUE_FIXTURE_COMBOS, VALUE_FIXTURES
from tests.const import (
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


def set_test_config(test_context: TstContext,
    setup_mock_provider: bool = False,
) -> dict:
    result = test_context.hass.data[TEST_CONFIG] = {
        ATTR_SETUP_MOCK_PROVIDER: setup_mock_provider
    }


def get_mock_plugin(
    hassio_provider: str = None,
) -> dict:
    result = {
        ATTR_PLUGIN_MODULE: "tests._plugins.hassio_mock",
        ATTR_CONFIG: {} 
    }
    if hassio_provider:
        result[ATTR_CONFIG][ATTR_HASSIO_PROVIDER] = hassio_provider
    return result


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["hassio_restart_addon_test"])
async def test_hassio_plugin_api_restart_addon_invalid_provider(test_context: TstContext, workflow_name: str):
    addon = "addon_test"
    invalid_provider = "invalid"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)
    
    data = {
        ATTR_HASSIO_PROVIDER: invalid_provider,
    }

    await test_context.async_start_react([mock_plugin])
    await test_context.async_send_reaction_event(data=data)
    test_context.verify_plugin_data_not_sent()
    test_context.verify_has_log_error(f"1 - Hassio provider for '{invalid_provider}' not found")


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["hassio_restart_addon_test"])
@pytest.mark.parametrize(VALUE_FIXTURES, VALUE_FIXTURE_COMBOS)
async def test_hassio_plugin_api_restart_addon(test_context: TstContext, workflow_name: str, config_value: bool, event_value: bool):
    addon = "addon_test"
    mock_plugin = get_mock_plugin(
        hassio_provider=HASSIO_MOCK_PROVIDER if config_value else None
    )
    set_test_config(test_context,
        setup_mock_provider=True,
    )

    await test_context.async_start_react([mock_plugin])
    
    data_in = {
        ATTR_HASSIO_PROVIDER: HASSIO_MOCK_PROVIDER if event_value else None,
    }
    data_out = {
        ATTR_ADDON: addon,
    }

    await test_context.async_send_reaction_event(data=data_in)
    test_context.verify_has_no_log_issues()
    test_context.verify_plugin_data_sent()
    test_context.verify_plugin_data_content(data_out)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["hassio_restart_addon_test"])
async def test_hassio_plugin_generic_provider_restart_addon(test_context: TstContext, workflow_name: str):
    addon = "addon_test"
    mock_plugin = get_mock_plugin()
    set_test_config(test_context)

    await test_context.async_start_react([mock_plugin])

    data_out = {
        ATTR_ADDON: addon,
    }

    await test_context.async_send_reaction_event()
    test_context.verify_has_no_log_issues()
    test_context.verify_service_call_sent()
    test_context.verify_service_call_content(DOMAIN, SERVICE_ADDON_RESTART, data_out)
