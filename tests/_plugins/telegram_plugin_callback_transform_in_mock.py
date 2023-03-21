
from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.utils.struct import DynamicData
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(CallbackTransformInTaskTaskMock)


class CallbackTransformInTaskTaskMock(CallbackTransformInTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)