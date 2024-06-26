"""React task manager."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import importlib
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.const import (
    EVENT_STATE_CHANGED,
    SUN_EVENT_SUNRISE,
    SUN_EVENT_SUNSET,
)
from homeassistant.core import CALLBACK_TYPE, Event as HaEvent, HassJob, callback
from homeassistant.helpers.event import async_track_time_change, async_track_sunrise, async_track_sunset
from homeassistant.util.async_ import create_eager_task

from custom_components.react.const import (
    ATTR_ENTITY, 
    EVENT_REACT_REACTION,
)
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.tasks.filters import (
    ALL_EVENTTYPE_FILTER_STRATEGIES,
    ALL_REACTION_FILTER_STRATEGIES, 
    ALL_STATE_CHANGE_FILTER_STRATEGIES,
    EventFilter,
)
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.time import TimeData

if TYPE_CHECKING:
    from custom_components.react.base import ReactBase

TRACK_EVENT_CALLBACKS = "react_track_event_callbacks"
TRACK_EVENT_LISTENERS = "react_track_event_listeners"

TRACK_REACTION_CALLBACKS = "react_track_reaction_callbacks"
TRACK_REACTION_LISTENER = "react_track_reaction_listener"

TRACK_STATE_CHANGE_CALLBACKS = "react_track_state_change_callbacks"
TRACK_STATE_CHANGE_FILTERS = "react_track_state_change_filters"
TRACK_STATE_CHANGE_LISTENER = "react_track_state_change_listener"

TRACK_TIME_CALLBACKS = "react_track_time_callbacks"
TRACK_TIME_LISTENERS = "react_track_time_listeners"

ATTR_TIME_KEY = "time_key"
ATTR_time_key = "time_key"

_LOGGER = get_react_logger()


class ReactTaskManager:

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self._tasks: dict[str, ReactTask] = {}
        self._unloaders: dict[str, dict[str, TaskUnloader]] = {}


    @property
    def tasks(self) -> list[ReactTask]:
        return list(self._tasks.values())


    async def async_load(self) -> None:
        task_files_root = Path(__file__).parent

        def _import_all_plugin_modules() -> list[ModuleType]:
            modules: list[ModuleType] = []
            for module_file in task_files_root.rglob("*.py"):
                if module_file.name in ("__init__.py", "base.py", "filters.py", "manager.py", "default_task.py"):
                    continue
                parent = str(module_file.relative_to(task_files_root).parent).replace("/", ".")
                name = module_file.stem
                modules.append(importlib.import_module(f"{__package__}.{parent}.{name}"))
            return modules

        async def _setup_module(module: ModuleType):
            if task := await module.async_setup_task(react=self.react):
                self.register_task(task)

        modules = await self.react.hass.async_add_import_executor_job(_import_all_plugin_modules)
        await asyncio.gather(
            *(
                create_eager_task(_setup_module(module))
                for module in modules
            )
        )


    def unload(self):
        for task in list(self._tasks.values()):
            self.unload_task(task)


    def register_task(self, task: ReactTask):
        if not task.id in self._tasks:
            self._tasks[task.id] = task
            task.manager = self


    def start_task(self, task: ReactTask):
        task.on_start()
        if task.track_event_filter:
            self.track_event(task.track_event_filter, task)
        
        if task.track_reaction_filters:
            for filter in task.track_reaction_filters:
                self.track_reaction(filter, task)

        if task.track_state_change_filters:
            for filter in task.track_state_change_filters:
                self.track_state_change(filter, task)
        

    def untrack_key(self, task: ReactTask, track_key: str):
        if unloader := self._unloaders.get(task.id, {}).pop(track_key, None):
            unloader.unload()
        
    
    def wrap_unloader(self, callback: CALLBACK_TYPE, task_id: str, key: str):
        if not task_id in self._unloaders:
            self._unloaders[task_id] = {}
            
        if key in self._unloaders[task_id]:
            _LOGGER.error(f"task {task_id} already contains key {key}")
        else:
            self._unloaders[task_id][key] = TaskUnloader(callback, task_id, key)


    def unload_task(self, task: ReactTask):
        unloaders = self._unloaders.pop(task.id, {})
        for unloader in unloaders.values():
            unloader.unload()
        if task.id in self._tasks:
            self._tasks.pop(task.id)
            task.on_unload()


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
        self.execute_tasks(ReactTaskType.BLOCK)


    def execute_tasks(self, task_type: ReactTaskType) -> None:
        runtime_tasks = (task for task in self.tasks if task.task_type == task_type)
        for task in runtime_tasks:
            self.start_task(task)


    def track_event(self, filter: EventFilter, task: ReactTask):
        event_callbacks: dict[str, list[tuple[HassJob[[HaEvent], Any], EventFilter]]] = self.react.hass.data.setdefault(
            TRACK_EVENT_CALLBACKS, {}
        )
        event_listeners: dict[str, CALLBACK_TYPE] = self.react.hass.data.setdefault(
            TRACK_EVENT_LISTENERS, {}
        )

        if filter.event_type not in event_listeners:
            @callback
            def _async_reaction_dispatcher(ha_event: HaEvent) -> None:
                for key in [ strategy.get_event_key(ha_event) for strategy in ALL_EVENTTYPE_FILTER_STRATEGIES ]:
                    if key in event_callbacks:
                        for job,filter in event_callbacks[key][:]:
                            if filter.applies(ha_event):
                                try:
                                    self.react.hass.async_run_hass_job(job, ha_event)
                                except Exception:  # pylint: disable=broad-except
                                    _LOGGER.exception(f"Error while processing event for {key}")

            event_listeners[filter.event_type] = self.react.hass.bus.async_listen(
                filter.event_type,
                _async_reaction_dispatcher,
            )

        job = HassJob(task.execute_task, f"track reaction type {filter.filter_key}")

        event_callbacks.setdefault(filter.filter_key, []).append((job, filter))
        
        @callback
        def remove_listener() -> None:
            event_callbacks[filter.filter_key].remove((job, filter))
            if len(event_callbacks[filter.filter_key]) == 0:
                del event_callbacks[filter.filter_key]

            if not event_callbacks:
                event_listeners[filter.event_type]()
                del event_listeners[filter.event_type]
                if not event_listeners:
                    del self.react.hass.data[TRACK_EVENT_LISTENERS]

        self.wrap_unloader(remove_listener, task.id, filter.track_key)


    def track_reaction(self, filter: EventFilter, task: ReactTask):
        reaction_callbacks: dict[str, list[HassJob[[HaEvent], Any]]] = self.react.hass.data.setdefault(
            TRACK_REACTION_CALLBACKS, {}
        )

        if TRACK_REACTION_LISTENER not in self.react.hass.data:
            @callback
            def _async_reaction_dispatcher(ha_event: HaEvent) -> None:
                for key in [ strategy.get_event_key(ha_event) for strategy in ALL_REACTION_FILTER_STRATEGIES ]:
                    if key in reaction_callbacks:
                        for job in reaction_callbacks[key][:]:
                            try:
                                self.react.hass.async_run_hass_job(job, ha_event)
                            except Exception:  # pylint: disable=broad-except
                                _LOGGER.exception(f"Error while processing reaction for {key}")

            self.react.hass.data[TRACK_REACTION_LISTENER] = self.react.hass.bus.async_listen(
                EVENT_REACT_REACTION,
                _async_reaction_dispatcher,
            )

        job = HassJob(task.execute_task, f"track reaction type {filter.filter_key}")

        reaction_callbacks.setdefault(filter.filter_key, []).append(job)
        
        @callback
        def remove_listener() -> None:
            reaction_callbacks[filter.filter_key].remove(job)
            if len(reaction_callbacks[filter.filter_key]) == 0:
                del reaction_callbacks[filter.filter_key]

            if not reaction_callbacks:
                self.react.hass.data[TRACK_REACTION_LISTENER]()
                del self.react.hass.data[TRACK_REACTION_LISTENER]

        self.wrap_unloader(remove_listener, task.id, filter.track_key)


    def track_state_change(self, filter: EventFilter, task: ReactTask):
        state_change_callbacks: dict[str, list[tuple[HassJob[[HaEvent], Any], EventFilter]]] = self.react.hass.data.setdefault(
            TRACK_STATE_CHANGE_CALLBACKS, {}
        )

        if TRACK_STATE_CHANGE_LISTENER not in self.react.hass.data:
            @callback
            def _async_state_change_dispatcher(ha_event: HaEvent) -> None:
                for key in [ strategy.get_event_key(ha_event) for strategy in ALL_STATE_CHANGE_FILTER_STRATEGIES ]:
                    if key in state_change_callbacks:
                        for job,filter in state_change_callbacks[key][:]:
                            if filter.applies(ha_event):
                                try:
                                    self.react.hass.async_run_hass_job(job, ha_event)
                                except Exception:  # pylint: disable=broad-except
                                    _LOGGER.exception(f"Error while processing state change for {key}")

            self.react.hass.data[TRACK_STATE_CHANGE_LISTENER] = self.react.hass.bus.async_listen(
                EVENT_STATE_CHANGED,
                _async_state_change_dispatcher,
            )

        job = HassJob(task.execute_task, f"track state change {filter.filter_key}")

        state_change_callbacks.setdefault(filter.filter_key, []).append((job, filter))
        
        @callback
        def remove_listener() -> None:
            state_change_callbacks[filter.filter_key].remove((job, filter))
            if len(state_change_callbacks[filter.filter_key]) == 0:
                del state_change_callbacks[filter.filter_key]

            if not state_change_callbacks:
                self.react.hass.data[TRACK_STATE_CHANGE_LISTENER]()
                del self.react.hass.data[TRACK_STATE_CHANGE_LISTENER]

        self.wrap_unloader(remove_listener, task.id, filter.track_key)


    def track_sun(self,
        sun_event: str,
        track_key: str,
        task: ReactTask,
        offset: timedelta,
        offset_str: str,
    ):
        time_callbacks: dict[str, list[HassJob[[HaEvent], Any]]] = self.react.hass.data.setdefault(TRACK_TIME_CALLBACKS, {})
        time_listeners: dict[str, CALLBACK_TYPE] = self.react.hass.data.setdefault(TRACK_TIME_LISTENERS, {})
        time_key = f"{sun_event}|{offset_str}"

        if time_key not in time_listeners:

            @callback
            def _async_sun_dispatcher() -> None:
                if time_key in time_callbacks:
                    for job in time_callbacks[time_key][:]:
                        try:
                            self.react.hass.async_run_hass_job(job)
                        except Exception:  # pylint: disable=broad-except
                            _LOGGER.exception(f"Error while processing sun change for {time_key}")
        
            if sun_event == SUN_EVENT_SUNRISE:
                time_listeners[time_key] = async_track_sunrise(
                    self.react.hass,
                    _async_sun_dispatcher,
                    offset
                )
            if sun_event == SUN_EVENT_SUNSET:
                time_listeners[time_key] = async_track_sunset(
                    self.react.hass,
                    _async_sun_dispatcher,
                    offset
                )

        async def async_send_ha_event():
            await task.execute_task(HaEvent("time", data = {ATTR_time_key: time_key, ATTR_ENTITY: sun_event}))
        job = HassJob(async_send_ha_event, f"track sun change for {time_key}")

        time_callbacks.setdefault(time_key, []).append(job)

        @callback
        def remove_listener() -> None:
            time_callbacks[time_key].remove(job)
            if len(time_callbacks[time_key]) == 0:
                del time_callbacks[time_key]

            if not time_callbacks:
                time_listeners[time_key]()
                del time_listeners[time_key]
                if not time_listeners:
                    del self.react.hass.data[TRACK_TIME_LISTENERS]

        self.wrap_unloader(remove_listener, task.id, track_key)


    def track_time(self,
        time_data: TimeData,
        time_key: str,
        track_key: str,
        task: ReactTask,
        *args,
    ):
        time_callbacks: dict[str, list[HassJob[[HaEvent], Any]]] = self.react.hass.data.setdefault(
            TRACK_TIME_CALLBACKS, {}
        )
        time_listeners: dict[str, CALLBACK_TYPE] = self.react.hass.data.setdefault(
            TRACK_TIME_LISTENERS, {}
        )

        if time_key not in time_listeners:

            @callback
            def _async_time_dispatcher(time: datetime) -> None:
                if time_key in time_callbacks:
                    for job in time_callbacks[time_key][:]:
                        try:
                            self.react.hass.async_run_hass_job(job)
                        except Exception:  # pylint: disable=broad-except
                            _LOGGER.exception(f"Error while processing time change for {time_key}")

            time_listeners[time_key] = async_track_time_change(
                self.react.hass,
                _async_time_dispatcher,
                time_data.hour,
                time_data.minute,
                time_data.second
            )

        async def async_send_ha_event():
            await task.execute_task(HaEvent("time", data = {ATTR_TIME_KEY: time_key, ATTR_ENTITY: args[0]}))
        job = HassJob(async_send_ha_event, f"track time change for {time_key}")

        time_callbacks.setdefault(time_key, []).append(job)

        @callback
        def remove_listener() -> None:
            time_callbacks[time_key].remove(job)
            if len(time_callbacks[time_key]) == 0:
                del time_callbacks[time_key]

            if not time_callbacks:
                time_listeners[time_key]()
                del time_listeners[time_key]
                if not time_listeners:
                    del self.react.hass.data[TRACK_TIME_LISTENERS]

        self.wrap_unloader(remove_listener, task.id, track_key)


class TaskUnloader():
    def __init__(self, cancel_event: Callable[[], None], task_id: str, key: str ) -> None:
        self.cancel_event = cancel_event
        self.task_id = task_id
        self.key = key


    def unload(self):
        if self.cancel_event:
            self.cancel_event()
            self.cancel_event = None
