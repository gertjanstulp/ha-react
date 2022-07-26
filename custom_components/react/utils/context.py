from __future__ import annotations

from typing import TYPE_CHECKING

from .updatable import Updatable
from .signals import ReactSignalDataReader
from ..base import ReactBase

if TYPE_CHECKING:
    from ..lib.runtime import DynamicDataHandler

from ..const import (
    ATTR_ACTION,
    ATTR_ACTOR,
    ATTR_ENTITY,
    ATTR_TYPE
)

class TemplateContextDataProvider(Updatable):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)        


    def provide(self, context_data: dict):
        pass


class VariableContextDataProvider(TemplateContextDataProvider):
    def __init__(self, react: ReactBase, variable_handler: DynamicDataHandler) -> None:
        super().__init__(react)
        self.variable_handler = variable_handler
        variable_handler.on_update(self.async_update)


    def provide(self, context_data: dict):
        for name in self.variable_handler.names:
            context_data[name] = getattr(self.variable_handler.value_container, name)


class ActorTemplateContextDataProvider(TemplateContextDataProvider):
    def __init__(self, react: ReactBase, react_signal_data_reader: ReactSignalDataReader) -> None:
        super().__init__(react)
        self.react_signal_data_reader = react_signal_data_reader


    def provide(self, context_data: dict):
        actor_container = {
            ATTR_ENTITY: self.react_signal_data_reader.actor_entity,
            ATTR_TYPE: self.react_signal_data_reader.actor_type,
            ATTR_ACTION: self.react_signal_data_reader.actor_action,
        }
        context_data[ATTR_ACTOR] = actor_container


class TemplateContext(Updatable):
    def __init__(self, react: ReactBase, template_context_data_provider: TemplateContextDataProvider = None) -> None:
        super().__init__(react)
        self.runtime_variables = {}
        self.template_context_data_provider = template_context_data_provider
        if template_context_data_provider:
            template_context_data_provider.on_update(self.async_update)


    def build(self, template_context_data_provider: TemplateContextDataProvider = None):
        if self.template_context_data_provider:
            self.template_context_data_provider.provide(self.runtime_variables)
        if template_context_data_provider:
            template_context_data_provider.provide(self.runtime_variables)
            

    def destroy(self):
        super().destroy()
        if self.template_context_data_provider:
            self.template_context_data_provider.destroy()