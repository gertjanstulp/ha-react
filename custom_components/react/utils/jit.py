from __future__ import annotations

from typing import Any, Generic, Type, TypeVar
from homeassistant.const import ATTR_ID

from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template, is_template_string

from .struct import DynamicData, MultiItem
from .context import TemplateContext, TemplateContextDataProvider
from ..base import ReactBase

from ..const import (
    PROP_ATTR_TYPE_POSTFIX,
    PROP_TYPE_DEFAULT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
)

_JITTER_PROPERTY = "{}_jitter"

T = TypeVar('T', bound=DynamicData)


class JitHandler(Generic[T]):

    def __init__(self, react: ReactBase, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        self.react = react
        self.config_source = config_source
        self.tctx = tctx
        self.t_type = t_type

        self.jit_attrs = []

        for attr in config_source.names:
            self.add_jitter(attr, PROP_TYPE_SOURCE)


    def add_jitter(self, attr: str, type_converter: Any, default: Any = None):
        attr_value = getattr(self.config_source, attr, None)

        if isinstance(attr_value, MultiItem):
            handler = JitHandler[MultiItem](self.react, attr_value, self.tctx, MultiItem)
            self.set_jitter_prop(attr, MultiItemJitter(attr, handler))
        elif isinstance(attr_value, DynamicData):
            handler = JitHandler(self.react, attr_value, self.tctx)
            self.set_jitter_prop(attr, ObjectJitter(attr, handler))
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                handlers = [ JitHandler(self.react, item, self.tctx) for item in attr_value ]
                self.set_jitter_prop(attr, ListJitter(attr, handlers))
            else:
                pass
        elif attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_jitter_prop(attr, TemplatePropertyJitter(attr, Template(attr_value), type_converter, self.tctx, self.react))
                self.set_property_type(attr, PROP_TYPE_TEMPLATE)
            else:
                self.set_jitter_prop(attr, ValuePropertyJitter(attr, attr_value, type_converter))
                self.set_property_type(attr, PROP_TYPE_VALUE)
        else:
            self.set_jitter_prop(attr, ValuePropertyJitter(attr, default, type_converter))
            self.set_property_type(attr, PROP_TYPE_DEFAULT)
            
        self.jit_attrs.append(attr)

    
    def set_jitter_prop(self, attr: str, value: BaseJitter):
        jitter_prop = _JITTER_PROPERTY.format(attr)
        setattr(self, jitter_prop, value)
        

    def get_jitter_prop(self, attr: str) -> BaseJitter:
        jitter_prop = _JITTER_PROPERTY.format(attr)
        return getattr(self, jitter_prop, None)


    def set_property_type(self, attr: str, prop_type: str):
        type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
        setattr(self, type_prop, prop_type)


    def is_template(self, attr: str) -> bool:
        type_prop = f"_{attr}{PROP_ATTR_TYPE_POSTFIX}"
        return getattr(self, type_prop, PROP_TYPE_DEFAULT) == PROP_TYPE_TEMPLATE
        

    def render(self, template_context_data_provider: TemplateContextDataProvider) -> T:
        target = self.t_type()
        target.set(ATTR_ID, self.config_source.get(ATTR_ID))
        for attr in self.jit_attrs:
            self.get_jitter_prop(attr).render(target, template_context_data_provider)
        return target


class BaseJitter:

    def __init__(self, attr: str, type_converter: Any = None) -> None:
        self.attr = attr
        self.type_converter = type_converter


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        raise NotImplementedError()


class MultiItemJitter(BaseJitter):

    def __init__(self, attr: str, handler: JitHandler) -> None:
        super().__init__(attr)

        self.handler = handler


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        this_target = MultiItem()
        for attr in self.handler.jit_attrs:
            self.handler.get_jitter_prop(attr).render(this_target, template_context_data_provider)
        target.set(self.attr, this_target)


class ObjectJitter(BaseJitter):

    def __init__(self, attr: str, handler: JitHandler) -> None:
        super().__init__(attr)
        
        self.handler = handler


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider):
        this_target = DynamicData()
        for attr in self.handler.jit_attrs:
            self.handler.get_jitter_prop(attr).render(this_target, template_context_data_provider)
        if target:
            target.set(self.attr, this_target)


class ListJitter(BaseJitter):

    def __init__(self, attr: str, handlers: list[JitHandler]) -> None:
        super().__init__(attr)

        self.handlers = handlers


    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        this_targets = []
        for handler in self.handlers:
            this_target = DynamicData()
            this_targets.append(this_target)
            for attr in handler.jit_attrs:
                handler.get_jitter_prop(attr).render(this_target, template_context_data_provider)
        if target:
            target.set(self.attr, this_targets)


class ValuePropertyJitter(BaseJitter):
    
    def __init__(self, attr: str, value: Any, type_converter: Any = None) -> None:
        super().__init__(attr, type_converter)
        
        self.value = value

    
    def render(self, target: DynamicData, template_context_data_provider: TemplateContextDataProvider) -> Any:
        if self.value == None: return
        target.set(self.attr, self.type_converter(self.value) if self.type_converter else self.value)


class TemplatePropertyJitter(BaseJitter):

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
            runtime_variables = {}
            self.tctx.build(runtime_variables, template_context_data_provider)
            value = self.template.async_render(runtime_variables)
        except TemplateError as te:
            self.react.log.error(f"Config: Error rendering {self.attr}: {te}")
        target.set(self.attr, self.type_converter(value) if self.type_converter else value)
