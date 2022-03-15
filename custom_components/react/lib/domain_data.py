from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .. import const as co
from . import store as st
from . import reactor as rc
from . import workflow_entities as wo
from . import coordinator as cord
from . import reaction_entities as re

class DomainData:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass
        self.reset()

    def init_config(self, config: ConfigType):
        self._load_config(config)

    async def init_data(self, config_entry: ConfigEntry):
        self._store = await st.async_get_store(self._hass)
        self._coordinator = cord.ReactionStoreCoordinator(self._hass)
        self._workflow_entity_manager = wo.WorkflowEntityManager(self._hass)
        self._reaction_entity_manager = re.ReactionEntityManager(self._hass)
        self._reactor = rc.Reactor(self._hass)
        self._device_id = config_entry.unique_id

    def init_workflows(self, workflows):
        self._workflows = workflows

    def reset(self):
        self._store = None
        self._coordinator = None
        self._workflow_entity_manager = None
        self._reaction_entity_manager = None
        self._reactor = None
        self._device_id = None
        self._workflows = None

    def _load_config(self, config):
        self._domain_config = config.get(co.DOMAIN, {})

    @property
    def domain_config(self):
        return self._domain_config

    @property
    def store(self):
        return self._store

    @property
    def coordinator(self):
        return self._coordinator

    @property
    def workflow_entity_manager(self):
        return self._workflow_entity_manager

    @property
    def reaction_entity_manager(self):
        return self._reaction_entity_manager

    @property
    def reactor(self):
        return self._reactor

    @property
    def device_id(self):
        return self._device_id

    @property
    def workflows(self):
        return self._workflows