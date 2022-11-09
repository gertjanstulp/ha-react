from homeassistant.core import HomeAssistant
from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_PLUGIN_MODULE, DOMAIN

from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


async def test_react_call_service_reload(hass: HomeAssistant, react_component):
    mock_plugin = {ATTR_PLUGIN_MODULE: "tests._plugins.dummy_plugin_reload_service_mock"}
    await react_component.async_setup(None, plugins=[mock_plugin])
    react: ReactBase = hass.data[DOMAIN]

    tc = TstContext(hass, None)
    react.hass.data[TEST_CONTEXT] = tc
    
    await react_component.async_call_service_reload()
    await react.hass.async_block_till_done()
    tc.verify_plugin_task_unload_sent()
