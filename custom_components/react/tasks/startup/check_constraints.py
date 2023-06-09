from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.const import MINIMUM_HA_VERSION
from custom_components.react.enums import ReactDisabledReason
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.utils.version import version_left_higher_or_equal_then_right


async def async_setup_task(react: ReactBase) -> Task:
    return Task(react=react)


class Task(ReactTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
    

    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP
    

    def execute(self) -> None:
        self.task_logger.debug(f"Checking HA version")
        if not version_left_higher_or_equal_then_right(
            self.react.core.ha_version.string,
            MINIMUM_HA_VERSION,
        ):
            self.task_logger.critical(f"You need HA version {MINIMUM_HA_VERSION} or newer to use this integration.")
            self.react.disable_react(ReactDisabledReason.CONSTRAINTS)
