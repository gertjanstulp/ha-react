from homeassistant.const import SERVICE_RELOAD, SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import ServiceCall, callback
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.service import async_register_admin_service

from .. import WorkflowEntity
from ..base import ReactBase

from ..const import (
    DOMAIN, 
    SERVICE_TRIGGER_WORKFLOW
)


async def async_setup_component(react: ReactBase):
    # Enable workflow toggling
    component = EntityComponent(react.log, DOMAIN, react.hass)
    component.async_register_entity_service(SERVICE_TOGGLE, {}, "async_toggle")
    component.async_register_entity_service(SERVICE_TURN_ON, {}, "async_turn_on")
    component.async_register_entity_service(SERVICE_TURN_OFF, {}, "async_turn_off")

    @callback
    async def trigger_workflow_service_handler(entity: WorkflowEntity, service_call: ServiceCall):
        await entity.async_trigger(service_call.context)
    component.async_register_entity_service(SERVICE_TRIGGER_WORKFLOW, {}, trigger_workflow_service_handler)


    # Load workflow entities
    async def async_load():
        entities = []
        for workflow in react.configuration.workflow_config.workflows.values():
            entities.append(WorkflowEntity(workflow, react.runtime))
        if entities:
            await component.async_add_entities(entities)
    await async_load()


    # Enable reload option
    async def reload_service_handler(service_call: ServiceCall) -> None:
        # Unload workflow entities from component and reread configuration from file
        conf = await component.async_prepare_reload()
        if conf is None:
            conf = {DOMAIN: {}}

        # Reload configuration from file
        react.configuration.update_from_dict(
            {
                **conf[DOMAIN],
                "config": conf[DOMAIN],
            }
        )

        # Load new workflow entities
        await async_load()

        # Reload plugins
        react.plugin_factory.reload()

    async_register_admin_service(react.hass, DOMAIN, SERVICE_RELOAD, reload_service_handler)