from custom_components.react.base import ReactBase
from custom_components.react.plugin.factory import OutputBlockSetupCallback, PluginSetup
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.struct import DynamicData

from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


class Setup(PluginSetup[DynamicData]):
    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(DummyTask)
    

class DummyTask(OutputBlock[DynamicData]):

    def __init__(self, react: ReactBase):
        super().__init__(react, None)


    async def async_handle_event(self, react_event: ReactEvent):
        pass


    def on_unload(self):
        context: TstContext = self.react.hass.data[TEST_CONTEXT]
        context.register_plugin_task_unload(self.id)