from typing import Generic, Type, TypeVar, Union
from anyio import Any

from homeassistant.const import ATTR_ID
from homeassistant.core import Event as HaEvent, callback, HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import TrackTemplate, TrackTemplateResult, async_track_template_result
from homeassistant.helpers.template import Template, is_template_string

from custom_components.react.const import (
    PROP_TYPE_DEFAULT,
    PROP_TYPE_LIST,
    PROP_TYPE_MULTI_ITEM,
    PROP_TYPE_OBJECT,
    PROP_TYPE_SOURCE,
    PROP_TYPE_TEMPLATE,
    PROP_TYPE_VALUE,
    SIGNAL_TRACK_UPDATE
)
from custom_components.react.utils.context import TemplateContext
from custom_components.react.utils.destroyable import Destroyable
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData, MultiItem
from custom_components.react.utils.updatable import Updatable, callable_type

T = TypeVar('T', bound=DynamicData)

_LOGGER = get_react_logger()


class BaseTracker(Updatable):

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.hass = hass


    def start(self):
        pass


    @callback
    def async_refresh(self):
        pass


class CompositeTracker(BaseTracker, Generic[T], Destroyable):
    def __init__(self, hass: HomeAssistant, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData) -> None:
        super().__init__(hass)

        self.config_source = config_source
        self.keys = config_source.keys()
        self.tctx = tctx

        self.trackers: list[BaseTracker] = []
        self.value_container = t_type()
        if id := self.config_source.get(ATTR_ID):
            self.value_container.set(ATTR_ID, id)

        for attr in config_source.keys():
            self.add_tracker(attr, PROP_TYPE_SOURCE)


    def as_trace_dict(self) -> dict:
        return { name : self.value_container.get(name) for name in self.config_source.keys() }
    

    def add_tracker(self, attr: str, type_converter: Any, default: Any = None) -> None:
        attr_value = getattr(self.config_source, attr, None)
        
        if isinstance(attr_value, MultiItem):
            tracker = MultiItemTracker(self.hass, attr_value, self.tctx)
            self.set_property(attr, tracker.value_container, PROP_TYPE_MULTI_ITEM)
            self.trackers.append(tracker)
        elif isinstance(attr_value, DynamicData):
            tracker = ObjectTracker(self.hass, attr_value, self.tctx)
            self.set_property(attr, tracker.value_container, PROP_TYPE_OBJECT)
            self.trackers.append(tracker)
        elif isinstance(attr_value, list):
            if len(attr_value) > 0 and isinstance(attr_value[0], DynamicData):
                trackers = [ ObjectTracker(self.hass, item, self.tctx) for item in attr_value]
                self.set_property(attr, [ tracker.value_container for tracker in trackers ], PROP_TYPE_LIST)
                self.trackers.extend(trackers)
            else:
                pass
        elif attr_value is not None:
            if isinstance(attr_value, str) and is_template_string(attr_value):
                self.set_property(attr, None, PROP_TYPE_TEMPLATE)
                self.trackers.append(TemplatePropertyTracker(self.hass, self, attr, Template(attr_value, self.hass), type_converter, self.tctx, self.async_update))
            else:
                self.set_property(attr, attr_value, PROP_TYPE_VALUE)
        else:
            self.set_property(attr, default, PROP_TYPE_DEFAULT)


    def set_property(self, attr: str, value: Any, prop_type: str = None):
        if hasattr(self.value_container, attr) and getattr(self.value_container, attr) == value: 
            return
        self.value_container.set(attr, value)
        if prop_type:
            self.value_container.set_type(attr, prop_type)
        async_dispatcher_send(self.hass, SIGNAL_TRACK_UPDATE, self.value_container, attr)


    def start(self):
        if self.tctx:
            @callback
            def async_update_template_trackers(*args):
                for tracker in self.trackers:
                    tracker.async_refresh()
            self.tctx.on_update(async_update_template_trackers)
        
        for tracker in self.trackers:
            tracker.start()


    def destroy(self) -> None:
        super().destroy()
        for tracker in self.trackers:
            tracker.destroy()


class MultiItemTracker(CompositeTracker[MultiItem]):

    def __init__(self, hass: HomeAssistant, config_source: MultiItem, tctx: TemplateContext) -> None:
        super().__init__(hass, config_source, tctx, MultiItem)


class ObjectTracker(CompositeTracker[T], Generic[T]):

    def __init__(self, hass: HomeAssistant, config_source: DynamicData, tctx: TemplateContext, t_type: Type[T] = DynamicData, update_callable: callable_type = None) -> None:
        super().__init__(hass, config_source, tctx, t_type)
        if update_callable:
            self.on_update(update_callable)


class TemplatePropertyTracker(BaseTracker, Destroyable):
    
    def __init__(self, hass: HomeAssistant, owner: CompositeTracker, property: str, template: Template, type_converter: Any, tctx: TemplateContext, update_callback: callable_type = None):
        super().__init__(hass)
        self.owner = owner
        self.property = property
        self.template = template
        self.type_converter = type_converter
        self.tctx = tctx

        self.runtime_variables: dict = None

        template.hass = hass
        if update_callback:
            self.on_update(update_callback)


    def start(self):
        self.owner.set_property(self.property, None)
        self.runtime_variables = {}
        self.tctx.build(self.runtime_variables)
        self.track_templates = [TrackTemplate(self.template, self.runtime_variables)]
        self.result_info = async_track_template_result(self.hass, self.track_templates, self.async_update_template)
        self.async_refresh()

    
    def destroy(self) -> None:
        super().destroy()
        if self.result_info:
            self.result_info.async_remove()


    @callback
    def async_refresh(self):
        if self.result_info:
            self.tctx.build(self.runtime_variables)
            self.result_info.async_refresh()


    @callback
    def async_update_template(self, ha_event: Union[HaEvent, None], updates: list[TrackTemplateResult]):
        if updates and len(updates) > 0:
            result = updates.pop().result
            if isinstance(result, TemplateError):
                _LOGGER.error(f"Config: Error rendering {self.property}: {result}")
                return

            self.owner.set_property(self.property, self.type_converter(result))
            self.async_update(result)
