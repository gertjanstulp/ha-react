from datetime import datetime
from typing import Any, Awaitable, Callable, Union
import voluptuous as vol
from awesomeversion import AwesomeVersion

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, STATE_ON, __version__ as HAVERSION
from homeassistant.core import Context, CoreState, HomeAssistant, callback, CALLBACK_TYPE, Event as HassEvent
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.trace import trace_get
from homeassistant.loader import async_get_integration
from homeassistant.util.dt import parse_datetime, utcnow

from custom_components.react.runtime.runtime import ReactRuntime, WorkflowRuntime
from custom_components.react.runtime.snapshots import create_snapshot
from custom_components.react.utils.context import TemplateContext, VariableContextDataProvider
from custom_components.react.utils.destroyable import Destroyable
from custom_components.react.utils.events import ActionEvent
from custom_components.react.utils.jit import ObjectJitter
from custom_components.react.utils.struct import ActorRuntime, ReactorRuntime, StateRuntime
from custom_components.react.utils.track import ObjectTracker


from .base import ReactBase
from .plugin.plugin_factory import PluginFactory
from .lib.config import Actor, Reactor, Workflow
from .tasks.manager import ReactTaskManager
from .utils.data import ReactData
from .utils.logger import format_data, get_react_logger

from .const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_LAST_TRIGGERED,
    ATTR_TRIGGER,
    ATTR_TYPE,
    ATTR_WORKFLOW_ID,
    CONF_ENTITY_MAPS,
    CONF_PLUGINS,
    CONF_FRONTEND_REPO_URL,
    CONF_STENCIL,
    CONF_WORKFLOW,
    DEFAULT_INITIAL_STATE, 
    DOMAIN,
    EVENT_REACT_ACTION,
    PLUGIN_SCHEMA,
    SIGNAL_ACTION_HANDLER_CREATED,
    SIGNAL_ACTION_HANDLER_DESTROYED,
    SIGNAL_WAIT_FINISHED,
    STARTUP,
    STENCIL_SCHEMA, 
    WORKFLOW_SCHEMA,
)

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(DOMAIN, default={}): vol.Schema({
        vol.Optional(CONF_FRONTEND_REPO_URL): cv.string,
        vol.Optional(CONF_PLUGINS): vol.All(cv.ensure_list, [PLUGIN_SCHEMA]),
        vol.Optional(CONF_ENTITY_MAPS): vol.Any(dict, None),
        vol.Optional(CONF_WORKFLOW): vol.Any(WORKFLOW_SCHEMA, None),
        vol.Optional(CONF_STENCIL): vol.Any(STENCIL_SCHEMA, None),
    })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = get_react_logger()

AWAITABLE_TYPE = Awaitable[Any]

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

    _LOGGER.info(STARTUP, integration.version)

    clientsession = async_get_clientsession(hass)

    # Initialize react data
    react.data = ReactData(react=react)
    react.hass = hass
    react.integration = integration
    react.session = clientsession
    react.system.running = True
    react.task_manager = ReactTaskManager(react=react)
    react.version = integration.version
    react.plugin_factory = PluginFactory(react=react)
    react.runtime = ReactRuntime(hass)
    
    if react.core.ha_version is None:
        react.core.ha_version = AwesomeVersion(HAVERSION)

    await react.task_manager.async_load()
    react.plugin_factory.load_plugins()

    # Run startup sequence
    async def async_startup():
        react.enable_react()
        await react.task_manager.async_execute_startup_tasks()
        react.task_manager.execute_runtime_tasks()
        if react.system.disabled:
            return False

        _LOGGER.debug("Setup complete")

        return True

    return await async_startup()


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

    def __init__(self, workflow: Workflow, runtime: ReactRuntime):
        """Initialize a workflow."""
        self.workflow = workflow
        self.runtime = runtime

        self.is_enabled: bool = False
        self._attr_unique_id = workflow.id
        self._attr_name = workflow.name or workflow.id.capitalize().replace("_", " ")
        self._attr_icon = workflow.icon
        self._last_triggered: datetime = None
        self._destroyers: list[CALLBACK_TYPE] = None
        self._async_destroyers: list[AWAITABLE_TYPE] = None

        self._variable_tracker: ObjectTracker = None
        

    async def async_added_to_hass(self) -> None:
        """Startup with initial state or previous state."""
        _LOGGER.debug(f"Registry: Entity {self.entity_id} - added to registry")

        self._destroyers = []
        self._async_destroyers = []

        await super().async_added_to_hass()

        try:
            if not self.workflow.is_valid:
                self._attr_available = False
                return

            # Create a tracker for workflow variables
            self._variable_tracker = ObjectTracker(self.hass, self.workflow.variables, TemplateContext(self.hass))
            self.on_destroy(self._variable_tracker.destroy)
            self._variable_tracker.start()
            
            # Create a template context for other trackers/jitters that depend on variables
            self.tctx = TemplateContext(self.hass, VariableContextDataProvider(self.hass, self._variable_tracker))
            self.on_destroy(self.tctx.destroy)
            
            # Create trackers for all actors
            def create_actor_tracker(actor: Actor):
                actor_tracker = ObjectTracker[ActorRuntime](self.hass, actor, self.tctx, ActorRuntime)
                actor_tracker.start()

                def destroy_dispatch():
                    async_dispatcher_send(
                        self.hass, 
                        SIGNAL_ACTION_HANDLER_DESTROYED, 
                        self.workflow.id,
                        actor_tracker.value_container)
                self.on_destroy(destroy_dispatch)
                self.on_destroy(actor_tracker.destroy)
                
                async_dispatcher_send(
                    self.hass, 
                    SIGNAL_ACTION_HANDLER_CREATED,
                    self.workflow.id,
                    actor_tracker.value_container)

                return actor_tracker

            self.actor_trackers = [ create_actor_tracker(actor) for actor in self.workflow.actors ]

            # Create jitters for all reactors
            def create_reactor_jitter(reactor: Reactor):
                return ObjectJitter[ReactorRuntime](self.hass, reactor, self.tctx, ReactorRuntime)
            self.reactor_jitters = [ create_reactor_jitter(reactor) for reactor in self.workflow.reactors ]

            # Create the runtime and start listening for events
            self.runtime.create_workflow_runtime(self.workflow)
            async def async_destroy_runtime():
                await self.runtime.async_destroy_workflow_runtime(self.workflow.id)
            self.on_destroy_async(async_destroy_runtime)
            self.on_destroy(self.hass.bus.async_listen(EVENT_REACT_ACTION, self.async_handle))
        
            if state := await self.async_get_last_state():
                enable_workflow = state.state == STATE_ON
                last_triggered = state.attributes.get("last_triggered")
                if last_triggered is not None:
                    self._last_triggered = parse_datetime(last_triggered)
                _LOGGER.debug(f"Registry: Entity {self.entity_id} - setting state: {format_data(last_state=enable_workflow, enabled=state.state)}")
            else:
                enable_workflow = DEFAULT_INITIAL_STATE
                _LOGGER.debug(f"Registry: Entity {self.entity_id} - setting state (no last state found): {format_data(enabled=enable_workflow)}")
            
            if enable_workflow:
                await self.async_enable()
        
        except:
            _LOGGER.exception(f"Failed adding workflow entity {self.entity_id} to hass")
            self._attr_available = False
            await self.async_destroy()


    async def async_will_remove_from_hass(self):
        _LOGGER.debug(f"Registry: Entity {self.entity_id} - removing from registry")
        await self.async_destroy()
        

    def on_destroy(self, destroyer: CALLBACK_TYPE):
        self._destroyers.append(destroyer)


    def on_destroy_async(self, destroyer: AWAITABLE_TYPE):
        self._async_destroyers.append(destroyer)


    async def async_destroy(self):
        for destroyer in self._destroyers:
            destroyer()
        for destroyer in self._async_destroyers:
            await destroyer()
        self._destroyers.clear()
        self._async_destroyers.clear()


    @property
    def should_poll(self):
        """If entity should be polled."""
        return False


    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_TRIGGERED: self._last_triggered,
            ATTR_WORKFLOW_ID: self.workflow.id
        }


    @property
    def is_on(self) -> bool:
        return self.is_enabled


    @callback
    def async_turn_on(self, **kwargs: Any) -> None:
        self.hass.loop.create_task(self.async_enable())


    @callback
    def async_turn_off(self, **kwargs: Any) -> None:
        self.hass.loop.create_task(self.async_disable())

    
    async def async_enable(self):
        if not self.is_enabled:
            self.is_enabled = True
            await self.async_update_ha_state()
            _LOGGER.debug(f"Registry: Entity {self.entity_id} - enabled")

        self.runtime.start_workflow_runtime(self.workflow.id)
    
    
    async def async_disable(self):
        if self.is_enabled:
            self.is_enabled = False
            await self.async_update_ha_state()
            _LOGGER.debug(f"Registry: Entity {self.entity_id} - disabled")

        await self.runtime.async_stop_workflow_runtime(self.workflow.id)


    @callback
    async def async_handle(self, hass_event: HassEvent):
        action_event = ActionEvent(hass_event)
        
        for actor_tracker in self.actor_trackers:
            run = False
            actor_runtime = actor_tracker.value_container
            if (action_event.payload.entity in actor_runtime.entity and action_event.payload.type in actor_runtime.type):
                config_action = actor_runtime.action
                if config_action is None:
                    run = True   
                else:
                    run = action_event.payload.action in config_action
                
                if run and actor_runtime.data and len(actor_runtime.data) > 0 and not action_event.payload.data:
                    run = False

                if run and action_event.payload.data and actor_runtime.data:
                    match: bool
                    for data_item in actor_runtime.data:
                        match = True
                        for name in data_item.keys():
                            if not name in action_event.payload.data.keys() or action_event.payload.data.get(name) != data_item.get(name):
                                match = False
                                break
                        if match:
                            break

                    if not match:
                        run = False

            if run: 
                if self.is_enabled:
                    self._last_triggered = utcnow()
                    self.async_write_ha_state()

                    parent_id = None if hass_event.context is None else hass_event.context.id
                    hass_run_context = Context(parent_id=parent_id)
                    
                    entity_vars = None
                    if state := self.hass.states.get(self.entity_id):
                        entity_vars = state.as_dict()

                    await self.runtime.async_run(self.workflow.id, create_snapshot(self.hass, self._variable_tracker, actor_tracker, self.reactor_jitters, action_event), entity_vars, hass_run_context)
                else:
                    _LOGGER.debug(f"WorkflowEntity: {self.workflow.id} {actor_runtime.id} skipping (workflow is disabled)")


    @callback
    async def async_trigger(self, context: Context) -> None:
        # pick the first actor for now, should be dynamic
        actor_runtime = self.actor_trackers[0].value_container
        data = {
            ATTR_ENTITY: actor_runtime.entity.first_or_none,
            ATTR_TYPE: actor_runtime.type.first_or_none,
            ATTR_ACTION: actor_runtime.action.first_or_none if actor_runtime.action else ATTR_TRIGGER,
            ATTR_DATA: actor_runtime.data[0].as_dict() if actor_runtime.data and len(actor_runtime.data) > 0 else None,
        }
        await self.async_handle(HassEvent(EVENT_REACT_ACTION, data, context=context))
