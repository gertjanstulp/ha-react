from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging
import pathlib
import secrets
from typing import TYPE_CHECKING, Any, List, Union
from aiohttp import ClientSession
from awesomeversion import AwesomeVersion

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.loader import Integration

from .enums import ReactStage, ReactDisabledReason
from .exceptions import ReactException
from .lib.config import PluginConfiguration, WorkflowConfiguration
from .reactions.base import ReactReaction
from .reactions.dispatch import ReactDispatch
from .utils.logger import get_react_logger

from .const import (
    ICON,
    SIGNAL_ITEM_CREATED, 
    SIGNAL_ITEM_REMOVED, 
    SIGNAL_ITEM_UPDATED
)

if TYPE_CHECKING:
    from .tasks.manager import ReactTaskManager
    from .utils.data import ReactData
    from .plugin.plugin_factory import PluginFactory


@dataclass
class ReactCore:
    """React Core info."""

    config_path: Union[pathlib.Path, None] = None
    ha_version: Union[AwesomeVersion, None] = None


class ReactReactions:

    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self._reactions: list[ReactReaction] = []
        self._reactions_by_id: dict[str, ReactReaction] = {}
        
        
    @property
    def list_all(self) -> list[ReactReaction]:
        """Return a list of reactions."""
        return self._reactions


    def add(self, reaction: ReactReaction) -> None:
        if reaction.data.id:
            if self.is_added(reaction_id=reaction.data.id):
                self.update_by_id(reaction)
            else:
                self.id = None
        elif reaction.data.overwrite:
            self.update_by_workflow_id(reaction)
        else:
            self._add_new(reaction)


    def _add_new(self, reaction: ReactReaction) -> None:
        id = secrets.token_hex(3)
        while id in self._reactions_by_id:
            id = secrets.token_hex(3)
        reaction.data.id = id
        
        self.insert(reaction)
        async_dispatcher_send(self.react.hass, SIGNAL_ITEM_CREATED, reaction)


    def insert(self, reaction: ReactReaction) -> None:
        self._reactions.append(reaction)
        self._reactions_by_id[reaction.data.id] = reaction


    def update_by_id(self, reaction: ReactReaction) -> None:
        if not self.is_added(reaction_id=reaction.data.id):
            return
        existing_reaction = self.get_by_id(reaction.data.id)
        self.update(existing_reaction, reaction)


    def update_by_workflow_id(self, reaction: ReactReaction) -> None:
        existing_reactions = self.get_by_workflow_id(reaction.data.workflow_id)
        while existing_reactions:
            existing_reaction = existing_reactions.pop()
            if existing_reaction.data.reactor_id == reaction.data.reactor_id:
                self.delete(existing_reaction)
        self._add_new(reaction)


    def update(self, existing_reaction: ReactReaction, new_reaction: ReactReaction):
        existing_reaction.data.datetime = new_reaction.data.datetime
        if new_reaction.data.forward_action:
            existing_reaction.data.reactor_action = new_reaction.data.reactor_action
        async_dispatcher_send(self.react.hass, SIGNAL_ITEM_UPDATED, existing_reaction)


    def delete(self, reaction: ReactReaction) -> None:
        if not self.is_added(reaction_id=reaction.data.id):
            return

        reaction.cancel_schedule()
        self._reactions.remove(reaction)
        self._reactions_by_id.pop(reaction.data.id, None)
        async_dispatcher_send(self.react.hass, SIGNAL_ITEM_REMOVED, reaction)
        

    def is_added(self, reaction_id: Union[str, None] = None) -> bool:
        if reaction_id is not None:
            return reaction_id in self._reactions_by_id
        return False
    
    
    def get_reactions(self, before_datetime: datetime = None) -> List[ReactReaction]:
        res = []
        for reaction in self._reactions:
            if (not before_datetime or reaction.data.datetime < before_datetime):
                res.append(reaction)
        return res


    def get_by_id(self, reaction_id: str) -> ReactReaction:
        return self._reactions_by_id.get(reaction_id, None)


    def get_by_workflow_id(self, workflow_id: str) -> list[ReactReaction]: 
        result = []
        for reaction in self._reactions:
            if reaction.data.workflow_id == workflow_id:
                result.append(reaction)
        return result


    def reset_workflow_reaction(self, reaction: ReactReaction):
        existing_reactions = self.get_by_workflow_id(reaction.data.reset_workflow)
        if existing_reactions:
            for existing_reaction in existing_reactions:
                self.delete(existing_reaction)


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
    stage = ReactStage.SETUP
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
        self.dispatcher: Union[ReactDispatch, None] = None
        self.frontend_version: Union[str, None] = None
        self.hass: Union[HomeAssistant, None] = None
        self.integration: Union[Integration, None] = None
        self.log: logging.Logger = get_react_logger()
        self.reactions: Union[ReactReactions, None] = None 
        self.recuring_tasks = []
        self.session: Union[ClientSession, None] = None
        self.status = ReactStatus()
        self.system = ReactSystem()
        self.tasks: Union[ReactTaskManager, None] = None
        self.version: Union[str, None] = None
        self.plugin_factory: Union[PluginFactory, None] = None

    
    @property
    def integration_dir(self) -> pathlib.Path:
        """Return the React integration dir."""
        return self.integration.file_path


    async def async_set_stage(self, stage: Union[ReactStage, None]) -> None:
        """Set React stage."""
        if stage and self.stage == stage:
            return

        self.stage = stage
        if stage is not None:
            self.log.info("Stage changed: %s", self.stage)
            self.hass.bus.async_fire("react/stage", {"stage": self.stage})
            await self.tasks.async_execute_runtime_tasks()


    def disable_react(self, reason: ReactDisabledReason) -> None:
        if self.system.disabled_reason == reason:
            return

        self.system.disabled_reason = reason
        if reason != ReactDisabledReason.REMOVED:
            self.log.error("React is disabled - %s", reason)


    def enable_react(self) -> None:
        if self.system.disabled_reason is not None:
            self.system.disabled_reason = None
            self.log.debug("React is enabled")

    
    async def startup_tasks(self, _event=None) -> None:
        """Tasks that are started after setup."""
        await self.async_set_stage(ReactStage.STARTUP)
        self.status.startup = False

        self.hass.bus.async_fire("react/status", {})

        await self.async_set_stage(ReactStage.RUNNING)

        self.hass.bus.async_fire("react/reload", {"force": True})

        if queue_task := self.tasks.get("prosess_queue"):
            await queue_task.execute_task()

        self.hass.bus.async_fire("react/status", {})
