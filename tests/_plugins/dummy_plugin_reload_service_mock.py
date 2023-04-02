

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import Event
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    plugin_api.register_plugin_task(DummyTask)


class DummyTask(PluginReactionTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, None)

        
    async def async_execute_plugin(self, event: Event):
        pass


    def unload(self):
        context: TstContext = self.react.hass.data[TEST_CONTEXT]
        context.register_plugin_task_unload(self.id)