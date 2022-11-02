from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant

from custom_components.react.utils.events import ActionEventData
from custom_components.react.utils.updatable import Updatable

from custom_components.react.const import (
    ATTR_ACTOR,
    ATTR_EVENT,
    ATTR_ID,
)

if TYPE_CHECKING:
    from .track import ObjectTracker


class TemplateContextDataProvider(Updatable):
    
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)


    def provide(self, context_data: dict):
        pass


class VariableContextDataProvider(TemplateContextDataProvider):
    
    def __init__(self, hass: HomeAssistant, variable_tracker: ObjectTracker) -> None:
        super().__init__(hass)

        self.variable_tracker = variable_tracker
        variable_tracker.on_update(self.async_update)


    def provide(self, context_data: dict):
        for name in self.variable_tracker.names:
            context_data[name] = getattr(self.variable_tracker.value_container, name)


class ActorTemplateContextDataProvider(TemplateContextDataProvider):
    
    def __init__(self, hass: HomeAssistant, event_data: ActionEventData, actor_id: str) -> None:
        super().__init__(hass)
        
        self.event_data = event_data
        self.actor_id = actor_id


    def provide(self, context_data: dict):
        context_data[ATTR_EVENT] = self.event_data.as_dict() 
        context_data[ATTR_ACTOR] = {
            ATTR_ID: self.actor_id
        }


class TemplateContext(Updatable):
    
    def __init__(self, hass: HomeAssistant, template_context_data_provider: TemplateContextDataProvider = None) -> None:
        super().__init__(hass)
        
        self.template_context_data_provider = template_context_data_provider
        if template_context_data_provider:
            template_context_data_provider.on_update(self.async_update)


    def build(self, target: dict, template_context_data_provider: TemplateContextDataProvider = None) -> None:
        if self.template_context_data_provider:
            self.template_context_data_provider.provide(target)
        if template_context_data_provider:
            template_context_data_provider.provide(target)
            

    def destroy(self) -> None:
        super().destroy()
        if self.template_context_data_provider:
            self.template_context_data_provider.destroy()