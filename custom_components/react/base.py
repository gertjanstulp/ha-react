from __future__ import annotations

from dataclasses import dataclass, asdict, field
import logging
import pathlib
from typing import TYPE_CHECKING, Any, Union
from aiohttp import ClientSession
from awesomeversion import AwesomeVersion

from homeassistant.core import HomeAssistant
from homeassistant.loader import Integration


from custom_components.react.enums import ReactDisabledReason
from custom_components.react.exceptions import ReactException
from custom_components.react.config.config import PluginConfiguration, WorkflowConfiguration
from custom_components.react.runtime.runtime import ReactRuntime
from custom_components.react.utils.logger import get_react_logger

from .const import (
    ICON,
)

if TYPE_CHECKING:
    from custom_components.react.tasks.manager import ReactTaskManager
    from custom_components.react.utils.data import ReactData
    from custom_components.react.plugin.factory import PluginFactory
    from custom_components.react.utils.session import SessionManager


@dataclass
class ReactCore:
    """React Core info."""

    config_path: Union[pathlib.Path, None] = None
    ha_version: Union[AwesomeVersion, None] = None


class ReactConfiguration:
    """ReactConfiguration class."""

    config: dict[str, Any] = field(default_factory=dict)
    debug: bool = False
    frontend_compact: bool = False
    frontend_mode: str = "Grid"
    frontend_repo_url: str = ""
    frontend_repo: str = ""
    plugin_path: str = "www/community/"
    sidepanel_icon: str = ICON
    sidepanel_title: str = "React"
    theme_path: str = "themes/"
    theme: bool = False
    workflow_config = WorkflowConfiguration()
    plugin_config = PluginConfiguration()
    

    def to_json(self) -> str:
        """Return a json string."""
        return asdict(self)
        

    def update_from_dict(self, data: dict) -> None:
        """Set attributes from dicts."""
        if not isinstance(data, dict):
            raise ReactException("Configuration is not valid.")

        for key in data:
            self.__setattr__(key, data[key])

        self.workflow_config.load(self.config)
        self.plugin_config.load(self.config)


@dataclass
class ReactSystem:
    """React System info."""

    disabled_reason: Union[ReactDisabledReason, None] = None
    running: bool = False
    action: bool = False

    @property
    def disabled(self) -> bool:
        """Return if React is disabled."""
        return self.disabled_reason is not None


@dataclass
class ReactStatus:
    """ReactStatus."""

    startup: bool = True
    new: bool = False
    reloading_data: bool = False
    upgrading_all: bool = False


class ReactBase():
    
    def __init__(self) -> None:
        self.configuration = ReactConfiguration()
        self.core = ReactCore()
        self.data: Union[ReactData, None] = None
        self.frontend_version: Union[str, None] = None
        self.hass: Union[HomeAssistant, None] = None
        self.integration: Union[Integration, None] = None
        self.logger: logging.Logger = get_react_logger()
        self.session: Union[ClientSession, None] = None
        self.status = ReactStatus()
        self.system = ReactSystem()
        self.task_manager: Union[ReactTaskManager, None] = None
        self.session_manager: SessionManager | None = None
        self.version: Union[str, None] = None
        self.plugin_factory: Union[PluginFactory, None] = None
        self.runtime: Union[ReactRuntime, None] = None

    
    @property
    def integration_dir(self) -> pathlib.Path:
        """Return the React integration dir."""
        return self.integration.file_path


    def disable_react(self, reason: ReactDisabledReason) -> None:
        if self.system.disabled_reason == reason:
            return

        self.system.disabled_reason = reason
        if reason != ReactDisabledReason.REMOVED:
            self.logger.error("React is disabled - %s", reason)


    def enable_react(self) -> None:
        if self.system.disabled_reason is not None:
            self.system.disabled_reason = None
            self.logger.debug("React is enabled")


    async def async_shutdown(self) -> None:
        if self.runtime:
            await self.runtime.async_shutdown(is_hass_shutdown=True)
        if self.plugin_factory:
            self.plugin_factory.unload_plugins()
        if self.task_manager:
            self.task_manager.unload()