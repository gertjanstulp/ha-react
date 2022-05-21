""""Starting setup task: Sensor"."""
from __future__ import annotations

from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.helpers.discovery import async_load_platform

from .base import ReactTask
from ..base import ReactBase
from ..enums import ReactStage

from ..const import (
    DOMAIN,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """Setup the React sensor platform."""

    stages = [ReactStage.SETUP]

    async def async_execute(self) -> None:
        """Execute the task."""
        self.react.hass.async_create_task(
            async_load_platform(self.react.hass, PLATFORM, DOMAIN, None, self.react.configuration.config)
        )
