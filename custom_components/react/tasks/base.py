from enum import Enum
from typing import TYPE_CHECKING, Callable
import uuid

from custom_components.react.base import ReactBase
from custom_components.react.tasks.filters import EventFilter
from custom_components.react.utils.logger import get_react_logger

if TYPE_CHECKING:
    from custom_components.react.tasks.manager import ReactTaskManager


class ReactTaskType(str, Enum):
    STARTUP = "startup"
    RUNTIME = "runtime"
    BLOCK = "block"


class ReactTask:
    """React task base."""

    def __init__(self, react: ReactBase, skip_task_log: bool = False) -> None:
        self.react = react
        self.skip_task_log = skip_task_log
        self.id = uuid.uuid4().hex
        self.task_logger = get_react_logger()
    
        self.track_event_filters: list[EventFilter] | None = None
        self.track_state_change_filters: list[EventFilter] | None = None
        self.track_reaction_filters: list[EventFilter] | None = None

        self.block_filter: Callable[..., bool] = None

        self.manager: ReactTaskManager = None


    @property
    def task_type(self) -> ReactTaskType:
        raise NotImplementedError()


    # def register_unloader(self):


    async def execute_task(self, *args, **kwargs) -> None:
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
            self.task_logger.exception(f"Executing task failed:")


    def unload(self):
        self.react.task_manager.unload_task(self)
        

    def on_unload(self):
        pass


    def on_start(self):
        pass