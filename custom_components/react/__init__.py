from typing import Any, Union
import voluptuous as vol
from awesomeversion import AwesomeVersion

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, STATE_ON, __version__ as HAVERSION
from homeassistant.core import Context, CoreState, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.loader import async_get_integration
from homeassistant.util.dt import parse_datetime

from .base import ReactBase, ReactReactions
from .enums import ReactStage
from .plugin.plugin_factory import PluginFactory
from .lib.config import Workflow
from .lib.runtime import WorkflowRuntime
from .reactions.dispatch import ReactDispatch
from .tasks.manager import ReactTaskManager
from .utils.data import ReactData
from .utils.logger import format_data, get_react_logger

from .const import (
    ATTR_LAST_TRIGGERED,
    ATTR_WORKFLOW_ID,
    CONF_ENTITY_MAPS,
    CONF_PLUGIN,
    CONF_FRONTEND_REPO_URL,
    CONF_STENCIL,
    CONF_WORKFLOW,
    DEFAULT_INITIAL_STATE, 
    DOMAIN,
    ENTITY_ID_FORMAT,
    PLUGIN_SCHEMA,
    STARTUP,
    STENCIL_SCHEMA, 
    WORKFLOW_SCHEMA,
)

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(DOMAIN, default={}): vol.Schema({
        vol.Optional(CONF_FRONTEND_REPO_URL): cv.string,
        vol.Optional(CONF_PLUGIN): PLUGIN_SCHEMA,
        vol.Optional(CONF_ENTITY_MAPS): dict,
        vol.Optional(CONF_WORKFLOW): WORKFLOW_SCHEMA,
        vol.Optional(CONF_STENCIL): STENCIL_SCHEMA,
    })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = get_react_logger()


async def async_initialize_integration(
    hass: HomeAssistant,
    config: Union[dict[str, Any], None] = None,
) -> bool:

    """Initialize the integration"""

    hass.data[DOMAIN] = react = ReactBase()
    react.enable_react()

    # Load configuration from file
    if config is not None:
        if DOMAIN not in config:
            return True
        react.configuration.update_from_dict(
            {
                **config[DOMAIN],
                "config": config[DOMAIN],
            }
        )

    integration = await async_get_integration(hass, DOMAIN)

    await react.async_set_stage(None)

    react.log.info(STARTUP, integration.version)

    clientsession = async_get_clientsession(hass)

    # Initialize react data
    react.data = ReactData(react=react)
    react.dispatcher = ReactDispatch(react=react)
    react.hass = hass
    react.integration = integration
    react.reactions = ReactReactions(react=react)
    react.session = clientsession
    react.system.running = True
    react.tasks = ReactTaskManager(react=react)
    react.version = integration.version
    react.plugin_factory = PluginFactory(react=react)
    
    if react.core.ha_version is None:
        react.core.ha_version = AwesomeVersion(HAVERSION)

    await react.tasks.async_load()

    # Run startup sequence
    async def async_startup():
        """React startup tasks."""
        react.enable_react()

        await react.async_set_stage(ReactStage.SETUP)
        if react.system.disabled:
            return False

        # Setup startup tasks
        if react.hass.state == CoreState.running:
            async_call_later(react.hass, 5, react.startup_tasks)
        else:   
            react.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, react.startup_tasks)

        await react.async_set_stage(ReactStage.WAITING)
        react.log.debug("Setup complete, waiting for Home Assistant before startup tasks starts")

        return not react.system.disabled

    await async_startup()

    return True


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up this integration using yaml."""
    _LOGGER.debug("Init: setting up react domain")
    
    return await async_initialize_integration(hass=hass, config=config)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    _LOGGER.debug(f"Init: Migrating from version {config_entry.version}")
    return True


class WorkflowEntity(ToggleEntity, RestoreEntity):
    """Representation of a workflow."""

    def __init__(self, react: ReactBase, workflow: Workflow):
        """Initialize a workflow."""
        self.react = react
        self.entity_id = ENTITY_ID_FORMAT.format(workflow.id)
        self.workflow = workflow
        self.is_enabled = False


    @callback
    async def async_trigger(self, context: Context) -> None:
        await self.workflow_runtime.async_trigger(context)


    async def async_added_to_hass(self) -> None:
        """Startup with initial state or previous state."""
        self.react.log.debug(f"Registry: '{self.entity_id}' added to registry")

        await super().async_added_to_hass()

        self.workflow_runtime = WorkflowRuntime(self.react, self.workflow)
        self.workflow_runtime.on_update(self.async_write_ha_state)

        if state := await self.async_get_last_state():
            enable_workflow = state.state == STATE_ON
            last_triggered = state.attributes.get("last_triggered")
            if last_triggered is not None:
                self.workflow_runtime.last_triggered = parse_datetime(last_triggered)
            self.react.log.debug(f"Registry: '{self.entity_id}' setting state: {format_data(last_state=enable_workflow, enabled=state.state)}")
        else:
            enable_workflow = DEFAULT_INITIAL_STATE
            self.react.log.debug(f"Registry: '{self.entity_id}' setting state (no last state found): {format_data(enabled=enable_workflow)}")

        
        if enable_workflow:
            await self.async_enable()


    async def async_will_remove_from_hass(self):
        self.react.log.debug(f"Registry: '{self.entity_id}' removing from registry")
        self.workflow_runtime.destroy()
        del self.workflow_runtime


    @property
    def should_poll(self):
        """If entity should be polled."""
        return False


    @property
    def name(self):
        """Return the name of the variable."""
        return self.workflow.friendly_name
    

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        return self.workflow.icon


    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_TRIGGERED: self.workflow_runtime.last_triggered,
            ATTR_WORKFLOW_ID: self.workflow.id
        }


    @property
    def is_on(self) -> bool:
        return self.is_enabled


    @callback
    def async_turn_on(self, **kwargs: Any) -> None:
        self.react.hass.loop.create_task(self.async_enable())


    @callback
    def async_turn_off(self, **kwargs: Any) -> None:
        self.react.hass.loop.create_task(self.async_disable())

    
    async def async_enable(self):
        if self.is_enabled:
            return

        self.react.log.debug(f"Registry: '{self.entity_id}' enabled")
        self.is_enabled = True
        self.workflow_runtime.start()
        
        await self.async_update_ha_state()
    
    
    async def async_disable(self):
        if not self.is_enabled:
            return

        self.react.log.debug(f"Registry: '{self.entity_id}' disabled")
        self.is_enabled = False
        self.workflow_runtime.stop()

        await self.async_update_ha_state()