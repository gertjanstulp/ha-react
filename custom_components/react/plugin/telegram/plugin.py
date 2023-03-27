from custom_components.react.plugin.notify.const import (
    PLUGIN_NAME as NOTIFY_PLUGIN_NAME
)
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.const import SERVICE_TYPE
from custom_components.react.plugin.telegram.service import TelegramService
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Telegram plugin: Loading")
    plugin_api.register_plugin_task(CallbackTransformInTask)
    plugin_api.register_plugin_service(NOTIFY_PLUGIN_NAME, SERVICE_TYPE, TelegramService(plugin_api.react))
