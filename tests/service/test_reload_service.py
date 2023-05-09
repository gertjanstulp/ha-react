import pytest

from homeassistant.core import HomeAssistant
from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_PLUGIN_MODULE, DOMAIN

from tests.common import FIXTURE_WORKFLOW_NAME, TEST_CONTEXT
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["immediate"])
async def test_call_service_reload(test_context: TstContext, workflow_name: str):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.reload_service_mock"}
    await test_context.async_start_react(mock_plugin)
    
    await test_context.react_component.async_call_service_reload()
    await test_context.react.hass.async_block_till_done()
    test_context.verify_plugin_task_unload_sent()
