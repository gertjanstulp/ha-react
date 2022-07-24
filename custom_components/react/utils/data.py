from datetime import datetime
from homeassistant.components.input_datetime import ATTR_DATETIME
from homeassistant.core import callback

from .logger import get_react_logger
from .store import async_load_from_store, async_save_to_store
from ..base import ReactBase
from ..reactions.base import ReactReaction

from ..const import (
    ATTR_ACTOR_ACTION, 
    ATTR_ACTOR_ENTITY, 
    ATTR_ACTOR_ID, 
    ATTR_ACTOR_TYPE,
    ATTR_DATA, 
    ATTR_FORWARD_ACTION, 
    ATTR_OVERWRITE, 
    ATTR_REACTION_DATETIME, 
    ATTR_REACTOR_ACTION, 
    ATTR_REACTOR_ENTITY, 
    ATTR_REACTOR_ID, 
    ATTR_REACTOR_TYPE, 
    ATTR_RESET_WORKFLOW, 
    ATTR_WORKFLOW_ID,
)


DEFAULT_REACTION_DATA = (
    # ("id", None),
    (ATTR_DATETIME, None),
    (ATTR_WORKFLOW_ID, None),
    (ATTR_ACTOR_ID, None),
    (ATTR_ACTOR_ENTITY, None),
    (ATTR_ACTOR_TYPE, None),
    (ATTR_ACTOR_ACTION, None),
    (ATTR_REACTOR_ID, None),
    (ATTR_REACTOR_ENTITY, None),
    (ATTR_REACTOR_TYPE, None),
    (ATTR_REACTOR_ACTION, None),
    (ATTR_RESET_WORKFLOW, None),
    (ATTR_OVERWRITE, None),
    (ATTR_FORWARD_ACTION, None),
    (ATTR_DATA, None)
)


class ReactData:
    """ReactData class."""

    def __init__(self, react: ReactBase):
        """Initialize."""
        self.react = react
        self.content = {}


    async def async_write(self, force: bool = False) -> None:
        """Write content to the store files."""
        if not force and self.react.system.disabled:
            return

        self.react.log.debug("<ReactData async_write> Saving data")

        # React
        await async_save_to_store(
            self.react.hass,
            "react",
            {
                "view": self.react.configuration.frontend_mode,
                "compact": self.react.configuration.frontend_compact,
            },
        )
        await self._async_store_reaction_data()

    
    async def _async_store_reaction_data(self):
        """Store the main reactions file"""
        self.content = {}
        for reaction in self.react.reactions.list_all:
            await self.async_store_reaction_data(reaction)

        await async_save_to_store(self.react.hass, "reactions", self.content)


    async def async_store_reaction_data(self, reaction: ReactReaction):
        data = {}

        for key, default_value in DEFAULT_REACTION_DATA:
            if (value := reaction.data.__getattribute__(key)) != default_value:
                if isinstance(value, datetime):
                    value = datetime.timestamp(value)
                data[key] = value

        self.content[str(reaction.data.id)] = data


    async def async_restore(self):
        """Restore saved data."""
        self.react.status.new = False
        react = await async_load_from_store(self.react.hass, "react") or {}
        reactions = await async_load_from_store(self.react.hass, "reactions") or {}

        if not react and not reactions:
            # Assume new install
            self.react.status.new = True
            self.react.log.debug("<ReactData restore> Loading base reaction information")
            reactions = {}

        self.react.log.debug("<ReactData restore> Restore started")

        # React
        self.react.configuration.frontend_mode = react.get("view", "Grid")
        self.react.configuration.frontend_compact = react.get("compact", False)

        try:
            for entry, reaction_data in reactions.items():
                if entry == "0":
                    # Ignore repositories with ID 0
                    self.react.log.debug("<ReactData restore> Found reaction with ID %s - %s", entry, reaction_data)
                    continue
                self.async_restore_reaction(entry, reaction_data)
            self.react.log.debug("<ReactData restore> Restore done")
        except BaseException as exception:
            self.react.log.critical("<ReactData restore> [%s] Restore Failed!", exception, exc_info=exception)
            return False

        return True

    
    @callback
    def async_restore_reaction(self, entry: str, reaction_data: dict):
        reaction = ReactReaction(self.react)

        reaction.data.id = entry
        reaction.data.datetime = datetime.fromtimestamp(reaction_data.get(ATTR_REACTION_DATETIME))
        reaction.data.workflow_id = reaction_data.get(ATTR_WORKFLOW_ID)
        reaction.data.actor_id = reaction_data.get(ATTR_ACTOR_ID)
        reaction.data.actor_entity = reaction_data.get(ATTR_ACTOR_ENTITY)
        reaction.data.actor_type = reaction_data.get(ATTR_ACTOR_TYPE)
        reaction.data.actor_action = reaction_data.get(ATTR_ACTOR_ACTION)
        reaction.data.reactor_id = reaction_data.get(ATTR_REACTOR_ID)
        reaction.data.reactor_entity = reaction_data.get(ATTR_REACTOR_ENTITY)
        reaction.data.reactor_type = reaction_data.get(ATTR_REACTOR_TYPE)
        reaction.data.reactor_action = reaction_data.get(ATTR_REACTOR_ACTION)
        reaction.data.reset_workflow = reaction_data.get(ATTR_RESET_WORKFLOW)
        reaction.data.overwrite = reaction_data.get(ATTR_OVERWRITE)
        reaction.data.forward_action = reaction_data.get(ATTR_FORWARD_ACTION)
        reaction.data.data = reaction_data.get(ATTR_DATA)

        self.react.reactions.insert(reaction)
