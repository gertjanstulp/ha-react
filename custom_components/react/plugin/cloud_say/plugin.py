from custom_components.react.plugin.cloud_say.tasks.speek import SpeekTask
from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.cloud_say.api import Api


def setup_plugin(plugin_api: PluginApi):
    cloud_say_api = Api(plugin_api.react)

    plugin_api.register_default_task(SpeekTask)
