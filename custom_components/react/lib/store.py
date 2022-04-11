import secrets
import attr

from datetime import datetime
from collections import OrderedDict
from typing import Dict, MutableMapping, cast

from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import as_timestamp

from .. import const as co


DATA_REGISTRY = f"{co.DOMAIN}_storage"
STORAGE_KEY = f"{co.DOMAIN}.storage"

STORAGE_VERSION = 3
SAVE_DELAY = 1


@attr.s(slots=True, frozen=False)
class ReactionEntry:
    """Reaction storage Entry."""

    id = attr.ib(type=str, default=None)
    timestamp = attr.ib(type=str, default=None)
    workflow_id = attr.ib(type=str, default=None)
    actor_id = attr.ib(type=str, default=None)
    reactor_id = attr.ib(type=str, default=None)
    datetime = attr.ib(type=datetime, default=None)
    action = attr.ib(type=str, default=None)


    def sync(self, force: bool = False):
        if self.datetime and (not self.timestamp or force) :
            self.timestamp = as_timestamp(self.datetime)
        elif self.timestamp and not self.datetime:
            self.datetime = datetime.fromtimestamp(self.timestamp)


class ReactionStorage:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.reactions: MutableMapping[str, ReactionEntry] = {}
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)


    async def async_load(self) -> None:
        data = await self.store.async_load()
        reactions: "OrderedDict[str, ReactionEntry]" = OrderedDict()

        if data is not None:
            if co.ATTR_REACTIONS in data:
                for stored_entry in data[co.ATTR_REACTIONS]:
                    entry = ReactionEntry(**stored_entry)
                    entry.sync()
                    reactions[entry.id] = entry

        self.reactions = reactions

    
    def schedule_save(self) -> None:
        self.store.async_delay_save(self._data_to_save, SAVE_DELAY)


    async def async_save(self) -> None:
        await self.store.async_save(self._data_to_save())


    @callback
    def _data_to_save(self) -> dict:
        store_data = {co.ATTR_REACTIONS: []}

        for entry in self.reactions.values():
            store_data[co.ATTR_REACTIONS].append(attr.asdict(entry, filter=lambda attr, value: attr.name not in [co.ATTR_REACTION_DATETIME]))

        return store_data


    async def async_delete(self):
        co.LOGGER.warn("Store", "Removing react configuration data!")
        self.reactions = {}
        await self.store.async_remove()


    def has_reaction(self, id: str) -> bool:
        return id in self.reactions


    def get_reaction_by_id(self, id: str) -> ReactionEntry:
        if not id: return None
        return self.reactions.get(id)


    def get_reactions_by_workflow_id(self, workflow_id: str) -> list[ReactionEntry]: 
        result = []
        for (id, reaction) in self.reactions.items():
            if reaction.workflow_id == workflow_id:
                result.append(reaction)
        return result


    def get_reactions(self, before_datetime: datetime = None) -> Dict[str, ReactionEntry]:
        res = {}
        for (id, reaction) in self.reactions.items():
            if (not before_datetime or reaction.datetime < before_datetime):
                res[id] = reaction
        return res


    def add_reaction(self, reaction: ReactionEntry):

        if reaction.id:
            id = reaction.id
            reaction.id = None
            if id in self.reactions:
                return False
        else:
            id = secrets.token_hex(3)
            while id in self.reactions:
                id = secrets.token_hex(3)

        co.LOGGER.info("Store", "'{}' adding reaction to store: '{}'", reaction.workflow_id, id)
        
        reaction.id = id
        self.reactions[id] = reaction
        self.schedule_save()
        return True
    

    def update_reaction(self, reaction: ReactionEntry):
        co.LOGGER.info("Store", "'{}' found existing reaction in store, updating with new timestamp: '{}'", reaction.workflow_id, reaction.id)
        self.schedule_save()


    def delete_reaction(self, id: str) -> None:
        if id in self.reactions:
            reaction = self.reactions.pop(id)
            co.LOGGER.info("Store", "'{}' deleting reaction from store: '{}'", reaction.workflow_id, id)
            self.schedule_save()
        else:
            co.LOGGER.warn("Store", "Reaction not found in store while deleting: '{}'".format(id))


async def async_get_store(hass: HomeAssistant) -> ReactionStorage:
    task = hass.data.get(DATA_REGISTRY)

    if task is None:
        async def _load_reg() -> ReactionStorage:
            store = ReactionStorage(hass)
            await store.async_load()
            return store

        task = hass.data[DATA_REGISTRY] = hass.async_create_task(_load_reg())

    return cast(ReactionStorage, await task)