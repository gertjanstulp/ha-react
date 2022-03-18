from datetime import datetime
import logging
import secrets
from collections import OrderedDict
from typing import MutableMapping, cast

import attr
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.loader import bind_hass
from homeassistant.util.dt import as_timestamp

from .. import const as co

DATA_REGISTRY = f"{co.DOMAIN}_storage"
STORAGE_KEY = f"{co.DOMAIN}.storage"

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 3
SAVE_DELAY = 3

@attr.s(slots=True, frozen=False)
class ReactionEntry:
    """Reaction storage Entry."""

    reaction_id = attr.ib(type=str, default=None)
    reactor = attr.ib(type=str, default=None)
    reactor_type = attr.ib(type=str, default=None)
    reactor_action = attr.ib(type=str, default=None)
    reaction_timestamp = attr.ib(type=str, default=None)
    workflow_id = attr.ib(type=str, default=None)
    reaction_datetime = attr.ib(type=datetime, default=None)

    def sync(self, force: bool = False):
        if self.reaction_datetime and (not self.reaction_timestamp or force) :
            self.reaction_timestamp = as_timestamp(self.reaction_datetime)
        elif self.reaction_timestamp and not self.reaction_datetime:
            self.reaction_datetime = datetime.fromtimestamp(self.reaction_timestamp)

class ReactionStorage:
    """Class to hold reaction data."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self.hass = hass
        self.reactions: MutableMapping[str, ReactionEntry] = {}
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self) -> None:
        """Load the registry of reaction entries."""
        data = await self._store.async_load()
        reactions: "OrderedDict[str, ReactionEntry]" = OrderedDict()

        if data is not None:
            if co.ATTR_REACTIONS in data:
                for stored_entry in data[co.ATTR_REACTIONS]:
                    entry = ReactionEntry(**stored_entry)
                    entry.sync()
                    reactions[entry.reaction_id] = entry

        self.reactions = reactions
    
    @callback
    def async_schedule_save(self) -> None:
        """Schedule saving the registry of reactions."""
        self._store.async_delay_save(self._data_to_save, SAVE_DELAY)

    async def async_save(self) -> None:
        """Save the registry of reactions."""
        await self._store.async_save(self._data_to_save())

    @callback
    def _data_to_save(self) -> dict:
        """Return data for the registry for reactions to store in a file."""
        store_data = {co.ATTR_REACTIONS: []}

        for entry in self.reactions.values():
            store_data[co.ATTR_REACTIONS].append(attr.asdict(entry, filter=lambda attr, value: attr.name not in [co.ATTR_REACTION_DATETIME]))

        return store_data

    async def async_delete(self):
        """Delete config."""
        _LOGGER.warning("Removing react configuration data!")
        self.reactions = {}
        await self._store.async_remove()

    def has_reaction(self, reaction_id) -> bool:
        return reaction_id in self.reactions

    def async_get_reaction_by_id(self, reaction_id: str) -> ReactionEntry:
        if not reaction_id: return None
        return self.reactions.get(reaction_id)

    def async_get_reaction_by_workflow_id(self, workflow_id: str) -> ReactionEntry: 
        for (id, reaction) in self.reactions.items():
            if reaction.workflow_id == workflow_id:
                return reaction
        return None 

    @callback
    def async_get_reactions(self, before_datetime: datetime = None) -> dict:
        """Get existing reactions."""
        res = {}
        for (id, reaction) in self.reactions.items():
            if (not before_datetime or reaction.reaction_datetime < before_datetime):
                res[id] = reaction
        return res

    @callback
    def async_add_reaction(self, reaction: ReactionEntry):
        """Create a new ReactionEntry."""
        co.LOGGER.info("Workflow '{}' adding new reaction to store".format(reaction.workflow_id))

        if reaction.reaction_id:
            reaction_id = reaction.reaction_id
            reaction.reaction_id = None
            if reaction_id in self.reactions:
                return False
        else:
            reaction_id = secrets.token_hex(3)
            while reaction_id in self.reactions:
                reaction_id = secrets.token_hex(3)
        
        reaction.reaction_id = reaction_id
        self.reactions[reaction_id] = reaction
        self.async_schedule_save()
        return True
    
    @callback
    def async_update_reaction(self, reaction: ReactionEntry):
        co.LOGGER.info("Workflow '{}' found existing reaction '{}' in store, updating with new timestamp".format(reaction.workflow_id, reaction.reaction_id))
        self.async_schedule_save()

    @callback
    def async_delete_reaction(self, reaction_id: str) -> None:
        """Delete ReactionEntry."""
        if reaction_id in self.reactions:
            del self.reactions[reaction_id]
            self.async_schedule_save()
        else:
            co.LOGGER.warn("Reaction '{}' not found in store while deleting".format(reaction_id))

@bind_hass
async def async_get_store(hass: HomeAssistant) -> ReactionStorage:
    """Return React storage instance."""
    task = hass.data.get(DATA_REGISTRY)

    if task is None:
        async def _load_reg() -> ReactionStorage:
            registry = ReactionStorage(hass)
            await registry.async_load()
            return registry

        task = hass.data[DATA_REGISTRY] = hass.async_create_task(_load_reg())

    return cast(ReactionStorage, await task)