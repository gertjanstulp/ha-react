from __future__ import annotations

from ..base import ReactTask

from ...base import ReactBase
from ...const import MINIMUM_HA_VERSION
from ...enums import ReactDisabledReason, ReactStage
from ...utils.version import version_left_higher_or_equal_then_right


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Check env Constraints."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        
        self.stages = [ReactStage.SETUP]


    def execute(self) -> None:
        """Execute the task."""

        if not version_left_higher_or_equal_then_right(
            self.react.core.ha_version.string,
            MINIMUM_HA_VERSION,
        ):
            self.task_logger(
                self.react.log.critical,
                f"You need HA version {MINIMUM_HA_VERSION} or newer to use this integration.",
            )
            self.react.disable_react(ReactDisabledReason.CONSTRAINTS)
