from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.mobile_app.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(CallbackTransformInTask)
