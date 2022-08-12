"""React task manager."""
from __future__ import annotations

import asyncio
from importlib import import_module
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Union

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .base import ReactTask

if TYPE_CHECKING:
    from ..base import ReactBase


class ReactTaskManager:
    """React task manager."""

    def __init__(self, react: ReactBase) -> None:
        """Initialize the setup manager class."""
        self.react = react
        self.__tasks: dict[str, ReactTask] = {}


    @property
    def tasks(self) -> list[ReactTask]:
        """Return all list of all tasks."""
        return list(self.__tasks.values())


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
                self.__tasks[task.slug] = task

        await asyncio.gather(*[_load_module(task) for task in task_modules])
        self.react.log.debug("Loaded %s tasks", len(self.tasks))

        schedule_tasks = len(self.react.recuring_tasks) == 0

        for task in self.tasks:
            if task.events is not None:
                for event in task.events:
                    self.react.hass.bus.async_listen_once(event, task.execute_task)
            
            if task.events_with_filters is not None:
                for event,filter in task.events_with_filters:
                    self.react.hass.bus.async_listen(event, task.execute_task, filter)

            if task.signals is not None:
                for signal in task.signals:
                    async_dispatcher_connect(self.react.hass, signal, task.execute_task)

            if task.schedule is not None and schedule_tasks:
                self.react.log.debug(
                    "Scheduling ReactTask<%s> to run every %s", task.slug, task.schedule
                )
                self.react.recuring_tasks.append(
                    self.react.hass.helpers.event.async_track_time_interval(
                        task.execute_task, task.schedule
                    )
                )


    def get(self, slug: str) -> Union[ReactTask, None]:
        """Return a task."""
        return self.__tasks.get(slug)


    async def async_execute_runtime_tasks(self) -> None:
        """Execute the execute methods of each runtime task if the stage matches."""
        await asyncio.gather(
            *(
                task.execute_task()
                for task in self.tasks
                if task.stages is not None and self.react.stage in task.stages
            )
        )
