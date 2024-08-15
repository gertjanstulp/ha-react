from __future__ import annotations

from homeassistant.core import ServiceCall

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.const import (
    ATTR_REACTION_ID, 
    ATTR_RUN_ID, 
    DOMAIN, 
    SERVICE_DELETE_REACTION, 
    SERVICE_DELETE_RUN, 
    SERVICE_REACT_NOW, 
    SERVICE_RUN_NOW
)


async def async_setup_task(react: ReactBase) -> Task:
    return Task(react=react)


class Task(ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.STARTUP


    async def async_execute(self) -> None:
        self.task_logger.debug("Setting up react service")
        self.react.hass.services.async_register(DOMAIN, SERVICE_RUN_NOW, self.async_run_now)
        self.react.hass.services.async_register(DOMAIN, SERVICE_REACT_NOW, self.async_react_now)
        self.react.hass.services.async_register(DOMAIN, SERVICE_DELETE_RUN, self.async_delete_run)
        self.react.hass.services.async_register(DOMAIN, SERVICE_DELETE_REACTION, self.async_delete_reaction)

    
    async def async_run_now(self, service_call: ServiceCall):
        try:
            run_id = service_call.data.get(ATTR_RUN_ID)
            self.react.runtime.run_now(run_id)
        except Exception as ex:
            self.task_logger.exception(ex, 'run_now failed')


    async def async_react_now(self, service_call: ServiceCall):
        try:
            reaction_id = service_call.data.get(ATTR_REACTION_ID)
            self.react.runtime.react_now(reaction_id)
        except Exception as ex:
            self.task_logger.exception(ex, 'react_now failed')
 

    async def async_delete_run(self, service_call: ServiceCall):
        try:
            run_id = service_call.data.get(ATTR_RUN_ID)
            self.react.runtime.delete_run(run_id)
        except Exception as ex:
            self.task_logger.exception(ex, 'delete_run failed')


    async def async_delete_reaction(self, service_call: ServiceCall):
        try:
            reaction_id = service_call.data.get(ATTR_REACTION_ID)
            self.react.runtime.delete_reaction(reaction_id)
        except Exception as ex:
            self.task_logger.exception(ex, 'delete_reaction failed')
