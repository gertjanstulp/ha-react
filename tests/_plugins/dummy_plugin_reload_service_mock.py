

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.tasks.defaults.default_task import DefaultTask
from custom_components.react.utils.events import Event
from custom_components.react.utils.struct import DynamicData
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(DummyTask)


class DummyTask(DefaultTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, None)

        
    async def async_execute_default(self, event: Event):
        pass


    def unload(self):
        context: TstContext = self.react.hass.data["test_context"]
        context.register_plugin_task_unload(self.id)