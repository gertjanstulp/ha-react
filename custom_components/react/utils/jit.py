from __future__ import annotations

from typing import Any, Generic, Type, TypeVar, Union

from homeassistant.const import ATTR_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template, is_template_string

from custom_components.react.utils.logger import get_react_logger

from .struct import DynamicData, MultiItem
from .context import TemplateContext, TemplateContextDataProvider

from ..const import (
    PROP_ATTR_TYPE_POSTFIX,
    PROP_TYPE_DEFAULT,
    PROP_TYPE_LIST,
    PROP_TYPE_MULTI_ITEM,
    PROP_TYPE_OBJECT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
)

_JITTER_PROPERTY = "{}_jitter"

T = TypeVar('T', bound=DynamicData)

_LOGGER = get_react_logger()

class BaseJitter:

    def __init__(self, type_converter: Any = None) -> None:
        self.type_converter = type_converter


    @property
    def prop_type(self):
        raise NotImplementedError


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        raise NotImplementedError()


class CompositeJitter(BaseJitter, Generic[T]):
    def __init__(self, hass: HomeAssistant, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        super().__init__()

        self.react = hass
        self.config_source = config_source
        self.tctx = tctx
        self.t_type = t_type

        self.jit_attrs = []

        for attr in config_source.keys():
            self.add_jitter(attr, PROP_TYPE_SOURCE)
        

    def add_jitter(self, attr: str, type_converter: Any, default: Any = None):
        attr_value = getattr(self.config_source, attr, None)

        if isinstance(attr_value, MultiItem):
            self.set_jitter(attr, MultiItemJitter(self.react, attr_value, self.tctx))
        elif isinstance(attr_value, DynamicData):
            self.set_jitter(attr, ObjectJitter(self.react, attr_value, self.tctx, self.t_type.type_hints.get(attr, DynamicData) if self.t_type.type_hints else DynamicData))
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                self.set_jitter(attr, ListJitter(self.react, attr_value, self.tctx))
            else:
                pass
        elif attr_value is not None:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_jitter(attr, TemplatePropertyJitter(attr, Template(attr_value), type_converter, self.tctx, self.react))
            else:
                self.set_jitter(attr, ValuePropertyJitter(attr_value, PROP_TYPE_VALUE, type_converter))
        else:
            self.set_jitter(attr, ValuePropertyJitter(default, PROP_TYPE_DEFAULT, type_converter))
            
        self.jit_attrs.append(attr)
    
    
    def set_jitter(self, attr: str, value: BaseJitter):
        jitter_prop = _JITTER_PROPERTY.format(attr)
        setattr(self, jitter_prop, value)

    
    def get_jitter(self, attr: str) -> Union[MultiItemJitter, ObjectJitter, ListJitter, ValuePropertyJitter, TemplatePropertyJitter]:
        jitter_prop = _JITTER_PROPERTY.format(attr)
        return getattr(self, jitter_prop, None)
 

    def render(self, template_context_data_provider: TemplateContextDataProvider):
        result = self.t_type()

        for attr in self.jit_attrs:
            jitter = self.get_jitter(attr)
            value = jitter.render(template_context_data_provider)
            if value != None: 
                result.set(attr, value)
                result.set_type(attr, jitter.prop_type)
                if hasattr(jitter, "template"):
                    result.set_template(attr, jitter.template.template)
        return result


class MultiItemJitter(CompositeJitter):

    def __init__(self, hass: HomeAssistant, config_source: DynamicData, tctx: TemplateContext) -> None:
        super().__init__(hass, config_source, tctx, MultiItem)


    @property
    def prop_type(self):
        return PROP_TYPE_MULTI_ITEM


class ObjectJitter(CompositeJitter[T], Generic[T]):

    def __init__(self, hass: HomeAssistant, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        super().__init__(hass, config_source, tctx, t_type)


    @property
    def prop_type(self):
        return PROP_TYPE_OBJECT


class ListJitter(BaseJitter):
    def __init__(self, hass: HomeAssistant, config_source: list[DynamicData], tctx: TemplateContext) -> None:
        super().__init__()

        self.react = hass
        self.config_source = config_source
        self.tctx = tctx
        self.jitters: list[ObjectJitter] = []

        for item in config_source:
            self.jitters.append(ObjectJitter(hass, item, tctx))


    @property
    def prop_type(self):
        return PROP_TYPE_LIST


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        result = []
        for jitter in self.jitters:
            result.append(jitter.render(template_context_data_provider))
        return result


class ValuePropertyJitter(BaseJitter):
    
    def __init__(self, value: Any, prop_type: str, type_converter: Any = None) -> None:
        super().__init__(type_converter)
        
        self.value = value
        self._prop_type = prop_type


    @property
    def prop_type(self):
        return self._prop_type

    
    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        if self.value == None: 
            return None
        return self.type_converter(self.value) if self.type_converter else self.value


class TemplatePropertyJitter(BaseJitter):

    def __init__(self, attr: str, template: Template, type_converter: Any, tctx: TemplateContext, hass: HomeAssistant):
        super().__init__(type_converter)

        self.hass = hass
        self.attr = attr
        self.template = template
        self.tctx = tctx

        template.hass = self.hass


    @property
    def prop_type(self):
        return PROP_TYPE_TEMPLATE


    def render(self, template_context_data_provider: TemplateContextDataProvider) -> Any:
        value = None
        try:
            runtime_variables = {}
            self.tctx.build(runtime_variables, template_context_data_provider)
            value = self.template.async_render(runtime_variables)
        except TemplateError as te:
            _LOGGER.error(f"Config: Error rendering {self.attr}: {te}")
        return self.type_converter(value) if self.type_converter else value
