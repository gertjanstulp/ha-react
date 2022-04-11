import asyncio

from homeassistant.components.sensor import DOMAIN as PLATFORM
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_RELOAD
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

from .. import const as co
from .config import ConfigManager
from .coordinator import Coordinator
from .reaction_entities import ReactionEntityManager
from .scheduler import Scheduler
from .transformer import TransformerManager
from .workflow_entities import WorkflowEntityManager
from .dispatcher import Dispatcher


class Bootstrapper:

    hass: HomeAssistant
    component: EntityComponent
    config_manager: ConfigManager
    dispatcher: Dispatcher
    coordinator: Coordinator
    reaction_entity_manager: ReactionEntityManager
    workflow_entity_manager: WorkflowEntityManager
    scheduler: Scheduler
    transformer_manager: TransformerManager


    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass


    def bootstrap(self, config: ConfigType) -> None:
        self.init_component()
        self.file_config = config
        
        self.config_manager = ConfigManager(self.hass)
        self.dispatcher = Dispatcher(self.hass)
        self.coordinator = Coordinator(self.hass)
        self.reaction_entity_manager = ReactionEntityManager(self.hass)
        self.workflow_entity_manager = WorkflowEntityManager(self.hass, self.component)
        self.scheduler = Scheduler(self.hass)
        self.transformer_manager = TransformerManager(self.hass)


    def init_component(self) -> None:
        self.component = EntityComponent(co.LOGGER, co.DOMAIN, self.hass)

        async def reload_service_handler(service_call: ServiceCall) -> None:
            await self.async_reload_config()

        async_register_admin_service(self.hass, co.DOMAIN, SERVICE_RELOAD, reload_service_handler)


    async def async_load(self, config_entry: ConfigEntry) -> None:
        # Start the scheduler and transformers
        self.scheduler.start()
        self.transformer_manager.start()

        # Initialize reaction backend
        await self.coordinator.async_init_store()
        
        # Load workflows from configuration file
        self.config_manager.load(self.file_config)

        # Load workflow entities
        await self.workflow_entity_manager.load()
        
        # Everything is started (except for the scheduler/transformers), so cleanup abandoned reaction entities which
        # were left behind in the store
        self.coordinator.cleanup_store()
        
        # Setup sensor platform for reactions. This will also initiate a load call on reaction_entity_manager
        self.hass.async_create_task(self.hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM))


    async def async_unload(self, config_entry: ConfigEntry) -> bool:
        self.dispatcher.stop()

        # Stop the scheduler and transformers
        self.transformer_manager.stop()
        self.scheduler.stop()

        # Unload sensor platform, which will unload all reaction entities
        unload_ok = all(await asyncio.gather(*[self.hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)]))
        
        # Unload all entities
        await self.workflow_entity_manager.unload()
        self.reaction_entity_manager.unload()

        # Unload configuration, which will also disable all template components
        self.config_manager.unload()

        return unload_ok


    async def async_reload_config(self) -> None:
        # Unload workflow entities from component and reread configuration from file
        conf = await self.component.async_prepare_reload()
        if conf is None:
            conf = {co.DOMAIN: {}}
        self.file_config = conf

        self.dispatcher.stop_tag(co.DISCONNECT_EVENT_TAG_CONFIG)

        # Reload configuration from file
        self.config_manager.reload(self.file_config)

        # Load new workflow entities
        await self.workflow_entity_manager.load()


    async def async_teardown(self) -> None:
        # Delete internal store data (react.storage)
        await self.coordinator.async_delete_config()

        self.dispatcher.clean()
        
        self.coordinator = None
        self.workflow_entity_manager = None
        self.reaction_entity_manager = None
        self.scheduler = None
        self.transformer_manager = None
        self.dispatcher = None


def get(hass: HomeAssistant) -> Bootstrapper:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER]
    ret = hass.data[co.DOMAIN_BOOTSTRAPPER] = Bootstrapper(hass)
    return ret
