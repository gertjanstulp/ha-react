from custom_components.react.plugin.mobile_app.const import SERVICE_TYPE
from custom_components.react.plugin.mobile_app.service import MobileAppService
from custom_components.react.plugin.mobile_app.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.plugin.notify.const import (
    PLUGIN_NAME as NOTIFY_PLUGIN_NAME
)
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Mobile_app plugin: Loading")
    plugin_api.register_plugin_task(CallbackTransformInTask)
    plugin_api.register_plugin_service(NOTIFY_PLUGIN_NAME, SERVICE_TYPE, MobileAppService(plugin_api.react))
