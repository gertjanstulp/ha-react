from typing import Dict, Tuple
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .. import const as co
from . import store as st
from . import scheduler as se
from . import workflow_entities as wo
from . import coordinator as cord
from . import reaction_entities as re
from . import config as cf
from . import transformer as tf

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
        self._scheduler = se.Scheduler(self._hass)
        self._transformer_manager = tf.TransformerManager(self._hass)
        self._device_id = config_entry.unique_id


    def init_workflows(self, workflows: Dict[str, cf.Workflow]):
        self._workflows = workflows


    def reset(self):
        self._store = None
        self._coordinator = None
        self._workflow_entity_manager = None
        self._reaction_entity_manager = None
        self._scheduler = None
        self._transformer_manager = None
        self._device_id = None
        self._workflows = None


    def _load_config(self, config):
        self._domain_config = config.get(co.DOMAIN, {})


    @property
    def domain_config(self):
        return self._domain_config


    @property
    def store(self) -> st.ReactionStorage:
        return self._store


    @property
    def coordinator(self) -> cord.ReactionStoreCoordinator:
        return self._coordinator


    @property
    def workflow_entity_manager(self) -> wo.WorkflowEntityManager:
        return self._workflow_entity_manager


    @property
    def reaction_entity_manager(self) -> re.ReactionEntityManager:
        return self._reaction_entity_manager


    @property
    def scheduler(self) -> se.Scheduler:
        return self._scheduler


    @property
    def transformer_manager(self) -> tf.TransformerManager:
        return self._transformer_manager


    @property
    def device_id(self) -> str:
        return self._device_id


    @property
    def workflows(self) -> Dict[str, cf.Workflow]:
        return self._workflows

    
    def get_workflow_metadata(self, reaction: st.ReactionEntry) -> Tuple[cf.Workflow, cf.Actor, cf.Reactor]:
        workflow = self._workflows.get(reaction.workflow_id, None)
        if workflow is None:
            co.LOGGER.warn("Workflow that created reaction '{}' no longer exists".format(reaction.id))
            return None, None, None

        actor = workflow.actors.get(reaction.actor_id, None)
        if actor is None:
            co.LOGGER.warn("Actor in workflow '{}' that created reaction '{}' no longer exists".format(workflow.id, reaction.id))
            return None, None, None

        reactor = workflow.reactors.get(reaction.reactor_id, None)
        if reactor is None:
            co.LOGGER.warn("Reactor in workflow '{}' that created reaction '{}' no longer exists".format(workflow.id, reaction.id))
            return None, None, None

        return workflow, actor, reactor


def get_domain_data(hass: HomeAssistant) -> DomainData:
    return hass.data[co.DOMAIN]


def set_domain_data(hass: HomeAssistant) -> DomainData:
    dd = DomainData(hass)
    hass.data[co.DOMAIN] = dd
    return dd
