from custom_components.react.plugin.cloud_say.speek_task import CloudSaySpeekTask
from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.cloud_say.api import Api

PLUGIN_NAME = "cloud_say"


def setup_plugin(api: PluginApi):
    cloud_say_api = Api(api.react)

    api.register_default_task(CloudSaySpeekTask)

