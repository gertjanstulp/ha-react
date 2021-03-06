from datetime import timedelta
from logging import Handler
from time import monotonic
from typing import Callable, Union

from homeassistant.core import Event

from ..base import ReactBase
from ..enums import ReactStage

class ReactTask:
    """React task base."""

    events: Union[list[str], None] = None
    events_with_filters: Union[list[tuple[str, Callable[[Event], bool]]], None] = None
    signals: Union[list[str], None] = None
    schedule: Union[timedelta, None] = None
    stages: Union[list[ReactStage], None] = None
    _can_run_disabled = False  ## Set to True if task can run while disabled


    def __init__(self, react: ReactBase) -> None:
        self.react = react


    @property
    def slug(self) -> str:
        """Return the check slug."""
        return self.__class__.__module__.rsplit(".", maxsplit=1)[-1]


    def task_logger(self, handler: Handler, msg: str) -> None:
        """Log message from task"""
        handler("ReactTask<%s> %s", self.slug, msg)


    async def execute_task(self, *args, **kwargs) -> None:
        """Execute the task defined in subclass."""
        if not self._can_run_disabled and self.react.system.disabled:
            self.task_logger(
                self.react.log.debug,
                f"Skipping task, React is disabled {self.react.system.disabled_reason}",
            )
            return
        self.task_logger(self.react.log.debug, "Executing task")
        start_time = monotonic()

        try:
            if task := getattr(self, "async_execute", None):
                await task(*args)  # pylint: disable=not-callable
            elif task := getattr(self, "execute", None):
                await self.react.hass.async_add_executor_job(task)

        except BaseException as exception:  # lgtm [py/catch-base-exception] pylint: disable=broad-except
            self.task_logger(self.react.log.error, f"failed: {exception}")

        else:
            self.react.log.debug(
                "ReactTask<%s> took %.3f seconds to complete", self.slug, monotonic() - start_time
            )
