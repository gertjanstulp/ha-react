from __future__ import annotations

from typing import TYPE_CHECKING


from .updatable import Updatable
from ..base import ReactBase
from ..utils.events import ActionEventDataReader

if TYPE_CHECKING:
    from .track import ObjectTracker

from ..const import (
    ATTR_ACTOR,
)

class TemplateContextDataProvider(Updatable):
    
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)        


    def provide(self, context_data: dict):
        pass


class VariableContextDataProvider(TemplateContextDataProvider):
    
    def __init__(self, react: ReactBase, variable_tracker: ObjectTracker) -> None:
        super().__init__(react)

        self.variable_tracker = variable_tracker
        variable_tracker.on_update(self.async_update)


    def provide(self, context_data: dict):
        for name in self.variable_tracker.names:
            context_data[name] = getattr(self.variable_tracker.value_container, name)


class ActorTemplateContextDataProvider(TemplateContextDataProvider):
    
    def __init__(self, react: ReactBase, event_reader: ActionEventDataReader) -> None:
        super().__init__(react)
        
        self.event_reader = event_reader


    def provide(self, context_data: dict):
        context_data[ATTR_ACTOR] = self.event_reader.to_dict()


class TemplateContext(Updatable):
    
    def __init__(self, react: ReactBase, template_context_data_provider: TemplateContextDataProvider = None) -> None:
        super().__init__(react)
        
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