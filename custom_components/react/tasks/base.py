from datetime import timedelta
from enum import Enum
from logging import Handler
from time import monotonic
from typing import Callable, Union
import uuid

from homeassistant.core import Event as HassEvent

from custom_components.react.utils.logger import get_react_logger

from ..base import ReactBase


_LOGGER = get_react_logger()


class ReactTaskType(str, Enum):
    STARTUP = "startup"
    RUNTIME = "runtime"
    PLUGIN = "plugin"


class ReactTask:
    """React task base."""

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.id = uuid.uuid4().hex
    
        self.event_types: Union[list[str], None] = None
        self.events_with_filters: Union[list[tuple[str, Callable[[HassEvent], bool]]], None] = None
        self.signals: Union[list[str], None] = None


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
            if task := getattr(self, "async_execute", None):
                await task(*args)  # pylint: disable=not-callable
            elif task := getattr(self, "execute", None):
                await self.react.hass.async_add_executor_job(task)

        except BaseException as exception:  # lgtm [py/catch-base-exception] pylint: disable=broad-except
            self.task_logger(_LOGGER.exception, f"failed:")

        else:
            _LOGGER.debug(
                "ReactTask<%s> took %.3f seconds to complete", self.slug, monotonic() - start_time
            )

    def unload(self):
        pass