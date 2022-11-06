from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultTask


class PluginApi():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    def register_default_task(self, task_type: type[DefaultTask]):
        self.react.task_manager.start_task(task_type(self.react))