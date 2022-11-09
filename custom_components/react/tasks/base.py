from datetime import timedelta
from logging import Handler
from time import monotonic
from typing import Callable, Union
import uuid

from homeassistant.core import Event as HassEvent

from ..base import ReactBase
from ..enums import ReactStage

class ReactTask:
    """React task base."""

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.id = uuid.uuid4().hex
    
        self.event_types: Union[list[str], None] = None
        self.events_with_filters: Union[list[tuple[str, Callable[[HassEvent], bool]]], None] = None
        self.signals: Union[list[str], None] = None
        self.schedule: Union[timedelta, None] = None
        self.stages: Union[list[ReactStage], None] = None
        self.can_run_disabled = False  ## Set to True if task can run while disabled


    @property
    def enabled(self) -> bool:
        return True


    @property
    def slug(self) -> str:
        """Return the check slug."""
        return self.__class__.__module__.rsplit(".", maxsplit=1)[-1]


    def task_logger(self, handler: Handler, msg: str) -> None:
        """Log message from task"""
        handler("ReactTask<%s> %s", self.slug, msg)


    async def execute_task(self, *args, **kwargs) -> None:
        """Execute the task defined in subclass."""
        if not self.can_run_disabled and self.react.system.disabled:
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
            self.task_logger(self.react.log.exception, f"failed:")

        else:
            self.react.log.debug(
                "ReactTask<%s> took %.3f seconds to complete", self.slug, monotonic() - start_time
            )

    def unload(self):
        pass