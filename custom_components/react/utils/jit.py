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


class BaseJitter:

    def __init__(self, type_converter: Any = None) -> None:
        self.type_converter = type_converter


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        raise NotImplementedError()


class CompositeJitter(BaseJitter, Generic[T]):
    def __init__(self, react: ReactBase, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        super().__init__()

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
            self.set_jitter_prop(attr, MultiItemJitter(self.react, attr_value, self.tctx))
        elif isinstance(attr_value, DynamicData):
            self.set_jitter_prop(attr, ObjectJitter(self.react, attr_value, self.tctx))
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                self.set_jitter_prop(attr, ListJitter(self.react, attr_value, self.tctx))
            else:
                pass
        elif attr_value:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_jitter_prop(attr, TemplatePropertyJitter(attr, Template(attr_value), type_converter, self.tctx, self.react))
                self.set_property_type(attr, PROP_TYPE_TEMPLATE)
            else:
                self.set_jitter_prop(attr, ValuePropertyJitter(attr_value, type_converter))
                self.set_property_type(attr, PROP_TYPE_VALUE)
        else:
            self.set_jitter_prop(attr, ValuePropertyJitter(default, type_converter))
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
 

    def render(self, template_context_data_provider: TemplateContextDataProvider):
        result = self.t_type()

        for attr in self.jit_attrs:
            value = self.get_jitter_prop(attr).render(template_context_data_provider)
            if value != None: 
                result.set(attr, value)
        return result


class MultiItemJitter(CompositeJitter):

    def __init__(self, react: ReactBase, config_source: DynamicData, tctx: TemplateContext) -> None:
        super().__init__(react, config_source, tctx, MultiItem)


class ObjectJitter(CompositeJitter[T], Generic[T]):

    def __init__(self, react: ReactBase, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        super().__init__(react, config_source, tctx, t_type)


class ListJitter(BaseJitter):
    def __init__(self, react: ReactBase, config_source: list[DynamicData], tctx: TemplateContext) -> None:
        super().__init__()

        self.react = react
        self.config_source = config_source
        self.tctx = tctx
        self.jitters: list[ObjectJitter] = []

        for item in config_source:
            self.jitters.append(ObjectJitter(react, item, tctx))


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        result = []
        for jitter in self.jitters:
            result.append(jitter.render(template_context_data_provider))
        return result


class ValuePropertyJitter(BaseJitter):
    
    def __init__(self, value: Any, type_converter: Any = None) -> None:
        super().__init__(type_converter)
        
        self.value = value

    
    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        if self.value == None: 
            return None
        return self.type_converter(self.value) if self.type_converter else self.value


class TemplatePropertyJitter(BaseJitter):

    def __init__(self, attr: str, template: Template, type_converter: Any, tctx: TemplateContext, react: ReactBase):
        super().__init__(type_converter)

        self.react = react
        self.attr = attr
        self.template = template
        self.tctx = tctx

        template.hass = self.react.hass


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        value = None
        try:
            runtime_variables = {}
            self.tctx.build(runtime_variables, template_context_data_provider)
            value = self.template.async_render(runtime_variables)
        except TemplateError as te:
            self.react.log.error(f"Config: Error rendering {self.attr}: {te}")
        return self.type_converter(value) if self.type_converter else value
