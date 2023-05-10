from datetime import timedelta
from enum import Enum
from logging import Handler
from time import monotonic
from typing import TYPE_CHECKING, Callable, Union
import uuid

from custom_components.react.base import ReactBase
from custom_components.react.tasks.filters import EventFilter
from custom_components.react.utils.logger import get_react_logger

if TYPE_CHECKING:
    from custom_components.react.tasks.manager import ReactTaskManager


_LOGGER = get_react_logger()


class ReactTaskType(str, Enum):
    STARTUP = "startup"
    RUNTIME = "runtime"
    BLOCK = "block"


class ReactTask:
    """React task base."""

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.id = uuid.uuid4().hex
    
        self.track_event_filters: list[EventFilter] | None = None
        self.track_state_change_filters: list[EventFilter] | None = None
        self.track_reaction_filters: list[EventFilter] | None = None

        self.block_filter: Callable[..., bool] = None

        self.manager: ReactTaskManager = None


    @property
    def task_type(self) -> ReactTaskType:
        raise NotImplementedError()


    @property
    def slug(self) -> str:
        """Return the check slug."""
        return self.__class__.__module__.rsplit(".", maxsplit=1)[-1]


    def task_logger(self, handler: Handler, msg: str) -> None:
        """Log message from task"""
        handler("ReactTask<%s> %s", self.slug, msg)


    async def execute_task(self, *args, **kwargs) -> None:
        """Execute the task defined in subclass."""
        self.task_logger(_LOGGER.debug, "Executing task")
        start_time = monotonic()

        try:
            proceed = True
            if self.block_filter:
                proceed = self.block_filter(*args, **kwargs)

            if proceed:
                if task := getattr(self, "async_execute", None):
                    await task(*args, **kwargs)  # pylint: disable=not-callable
                elif task := getattr(self, "execute", None):
                    await self.react.hass.async_add_executor_job(task, *args)

        except BaseException as exception:  # lgtm [py/catch-base-exception] pylint: disable=broad-except
            self.task_logger(_LOGGER.exception, f"failed:")

        else:
            _LOGGER.debug(
                "ReactTask<%s> took %.3f seconds to complete", self.slug, monotonic() - start_time
            )


    def unload(self):
        self.react.task_manager.unload_task(self)
        

    def on_unload(self):
        pass