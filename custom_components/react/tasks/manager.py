"""React task manager."""
from __future__ import annotations


import asyncio
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Union

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_interval

from custom_components.react.tasks.base import ReactTask, ReactTaskType

if TYPE_CHECKING:
    from custom_components.react.base import ReactBase


class ReactTaskManager:
    """React task manager."""

    def __init__(self, react: ReactBase) -> None:
        """Initialize the setup manager class."""
        self.react = react
        self._tasks: dict[str, ReactTask] = {}
        self._unloaders: dict[str, TaskUnloader] = {}


    @property
    def tasks(self) -> list[ReactTask]:
        """Return all list of all tasks."""
        return list(self._tasks.values())


    async def async_load(self) -> None:
        """Load all tasks."""
        task_files_root = Path(__file__).parent
        task_modules = (
            {
                "parent": str(module.relative_to(task_files_root).parent).replace("/", "."),
                "name": module.stem,
            }
            for module in task_files_root.rglob("*.py")
            if module.name not in ("base.py", "__init__.py", "manager.py", "transform_base.py", "default_task.py")
        )

        async def _load_module(module: dict):
            task_module = import_module(f"{__package__}.{module['parent']}.{module['name']}")
            if task := await task_module.async_setup_task(react=self.react):
                self._tasks[task.id] = task

        await asyncio.gather(*[_load_module(task) for task in task_modules])
        self.react.log.debug("Loaded %s tasks", len(self.tasks))


    def register_task(self, task: ReactTask):
        if not task.id in self._tasks:
            self._tasks[task.id] = task


    def start_task(self, task: ReactTask):
        if task.event_types is not None:
            for event_type in task.event_types:
                cancel = self.react.hass.bus.async_listen_once(event_type, task.execute_task)
                self._unloaders[task.id] = TaskUnloader(cancel)
        
        if task.events_with_filters is not None:
            for event_type,filter in task.events_with_filters:
                cancel = self.react.hass.bus.async_listen(event_type, task.execute_task, filter)
                self._unloaders[task.id] = TaskUnloader(cancel)

        if task.signals is not None:
            for signal in task.signals:
                cancel = async_dispatcher_connect(self.react.hass, signal, task.execute_task)
                self._unloaders[task.id] = TaskUnloader(cancel)

    
    def unload_task(self, task: ReactTask):
        unloader = self._unloaders.pop(task.id, None)
        if unloader:
            unloader.unload()
        if task.id in self._tasks:
            self._tasks.pop(task.id)
            task.unload()


    async def async_execute_startup_tasks(self) -> None:
        await asyncio.gather(
            *(
                task.execute_task()
                for task in self.tasks
                if task.task_type == ReactTaskType.STARTUP
            )
        )
    

    def execute_runtime_tasks(self) -> None:
        self.execute_tasks(ReactTaskType.RUNTIME)


    def execute_plugin_tasks(self) -> None:
        self.execute_tasks(ReactTaskType.PLUGIN)


    def execute_tasks(self, task_type: ReactTaskType) -> None:
        runtime_tasks = (task for task in self.tasks if task.task_type == task_type)
        for task in runtime_tasks:
            self.start_task(task)


class TaskUnloader():
    def __init__(self, cancel_event: Callable[[], None] ) -> None:
        self.cancel_event = cancel_event


    def unload(self):
        if self.cancel_event:
            self.cancel_event()
            self.cancel_event = None