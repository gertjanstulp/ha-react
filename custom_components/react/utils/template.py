from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union
from config.custom_components.react.utils.struct import DynamicData, MultiItem

from homeassistant.core import Event, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.event import TrackTemplate, TrackTemplateResult, async_track_template_result
from homeassistant.helpers.template import Template

from ..base import ReactBase
from .updatable import Updatable, callable_type
from .context import TemplateContext, TemplateContextDataProvider

if TYPE_CHECKING:
    from ..lib.runtime import RuntimeHandler, DynamicDataHandler


class BaseJitter:
    type_converter: Any
    attr: str


    def __init__(self, attr: str, type_converter: Any = None) -> None:
        self.attr = attr
        self.type_converter = type_converter


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        raise NotImplementedError()


class MultiItemJitter(BaseJitter):
    handler: DynamicDataHandler

    def __init__(self, attr: str, handler: DynamicDataHandler) -> None:
        super().__init__(attr)

        self.handler = handler


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        for attr in self.handler.jit_attrs:
            self.handler.get_jitter_prop(attr).render(self.handler.value_container, template_context_data_provider)
        target.set(self.attr, self.handler.value_container)


class ObjectJitter(BaseJitter):
    handler: DynamicDataHandler

    def __init__(self, attr: str, handler: DynamicDataHandler) -> None:
        super().__init__(attr)
        
        self.handler = handler


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider):
        for attr in self.handler.jit_attrs:
            self.handler.get_jitter_prop(attr).render(self.handler.value_container, template_context_data_provider)
        if target:
            target.set(self.attr, self.handler.value_container)


class ListJitter(BaseJitter):
    handlers: list[DynamicDataHandler]

    def __init__(self, attr: str, handlers: list[DynamicDataHandler]) -> None:
        super().__init__(attr)

        self.handlers = handlers


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        for handler in self.handlers:
            for attr in handler.jit_attrs:
                handler.get_jitter_prop(attr).render(handler.value_container, template_context_data_provider)
        if target:
            target.set(self.attr, [handler.value_container for handler in self.handlers])



class ValuePropertyJitter(BaseJitter):
    def __init__(self, attr: str, value: Any, type_converter: Any = None) -> None:
        super().__init__(attr, type_converter)
        
        self.value = value

    
    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        target.set(self.attr, self.type_converter(self.value) if self.type_converter else self.value)


class TemplatePropertyJitter(BaseJitter):
    react: ReactBase
    attr: str
    template: Template


    def __init__(self, attr: str, template: Template, type_converter: Any, tctx: TemplateContext, react: ReactBase):
        super().__init__(attr, type_converter)

        self.react = react
        self.attr = attr
        self.template = template
        self.tctx = tctx

        template.hass = self.react.hass


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider):
        value = None
        try:
            self.tctx.build(template_context_data_provider)
            value = self.template.async_render(self.tctx.runtime_variables)
        except TemplateError as te:
            self.react.log.error(f"Config: Error rendering {self.attr}: {te}")
        target.set(self.attr, self.type_converter(value) if self.type_converter else value)


class BaseTracker(Updatable):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)

    def start(self):
        pass


    @callback
    def async_refresh(self):
        pass


class MultiItemTracker(BaseTracker):
    property: str
    handler: DynamicDataHandler

    def __init__(self, react: ReactBase, property: str, handler: DynamicDataHandler) -> None:
        super().__init__(react)
        self.property = property
        self.handler = handler

    def start(self):
        self.handler.start_trackers()


class ObjectTracker(BaseTracker):
    property: str
    handler: DynamicDataHandler

    def __init__(self, react: ReactBase, property: str, handler: DynamicDataHandler) -> None:
        super().__init__(react)
        self.property = property
        self.handler = handler


    def start(self):
        self.handler.start_trackers()


class TemplatePropertyTracker(BaseTracker):
    
    owner: Union[RuntimeHandler, None] = None
    react: ReactBase
    property: str
    type_converter: Any
    template: Template
    tctx: Union[TemplateContext, None] = None


    def __init__(self, react: ReactBase, owner: RuntimeHandler, property: str, template: Template, type_converter: Any, tctx: TemplateContext, update_callback: callable_type = None):
        super().__init__(react)
        self.react = react
        self.owner = owner
        self.property = property
        self.template = template
        self.type_converter = type_converter
        self.tctx = tctx

        template.hass = react.hass
        if update_callback:
            self.on_update(update_callback)


    def start(self):
        self.owner.set_property(self.property, None)
        self.tctx.build()
        self.track_templates = [TrackTemplate(self.template, self.tctx.runtime_variables)]
        self.result_info = async_track_template_result(self.react.hass, self.track_templates, self.async_update_template)
        self.async_refresh()

    
    def destroy(self):
        if self.result_info:
            self.result_info.async_remove()


    @callback
    def async_refresh(self):
        if self.result_info:
            self.tctx.build()
            self.result_info.async_refresh()


    @callback
    def async_update_template(self, event: Union[Event, None], updates: list[TrackTemplateResult]):
        if updates and len(updates) > 0:
            result = updates.pop().result
            if isinstance(result, TemplateError):
                self.react.log.error(f"Config: Error rendering {self.property}: {result}")
                return

            self.owner.set_property(self.property, self.type_converter(result))
            self.async_update()
