"""React task manager."""
from __future__ import annotations


import asyncio
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Union

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_interval

from custom_components.react.tasks.base import ReactTask

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

        schedule_tasks = len(self.react.recuring_tasks) == 0

        for task in self.tasks:
            self.start_task(task, schedule_tasks)


    def start_task(self, task: ReactTask, schedule_tasks: bool = True):
        if not task.id in self._tasks:
            self._tasks[task.id] = task
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

        if task.schedule is not None and schedule_tasks:
            self.react.log.debug(
                "Scheduling ReactTask<%s> to run every %s", task.slug, task.schedule
            )

            cancel = async_track_time_interval(self.react.hass, task.execute_task, task.schedule)
            self.react.recuring_tasks.append(cancel)
            self._unloaders[task.id] = TaskUnloader(cancel)

    
    def stop_task(self, task_id: str):
        unloader = self._unloaders.pop(task_id, None)
        if unloader:
            unloader.unload()
        self._tasks.pop(task_id).unload()


    async def async_execute_runtime_tasks(self) -> None:
        """Execute the execute methods of each runtime task if the stage matches."""
        await asyncio.gather(
            *(
                task.execute_task()
                for task in self.tasks
                if task.stages is not None and self.react.stage in task.stages
            )
        )


class TaskUnloader():
    def __init__(self, cancel_event: Callable[[], None] ) -> None:
        self.cancel_event = cancel_event


    def unload(self):
        if self.cancel_event:
            self.cancel_event()
            self.cancel_event = None