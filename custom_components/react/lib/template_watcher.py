from typing import Any, Union
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.event import TrackTemplate, TrackTemplateResult, async_track_template_result
from homeassistant.helpers.template import Template

from .. import const as co

class TemplateWatcher:
    def __init__(self, hass: HomeAssistant, owner: Any, property: str, type_converter: Any, template: Template, variables: dict):
        self.owner = owner
        self.property = property
        self.type_converter = type_converter
        self.template = template
        self.variables = variables

        setattr(owner, property, None)

        self.result_info = async_track_template_result(hass, [TrackTemplate(template, variables)], self.update)

        self.async_refresh = self.result_info.async_refresh
        self.async_refresh()


    def register_entity(self, entity: Any):
        self.entity = entity
        entity.async_on_remove(self.async_remove)
        entity._async_update = self.async_refresh
        self.entity_ha_update = entity.async_write_ha_state


    def update(self, event: Union[Event, None], updates: list[TrackTemplateResult]):
        if updates and len(updates) > 0:
            result = updates.pop().result
            if isinstance(result, TemplateError):
                co.LOGGER.error("Error rendering %s %s: %s", self.property, self.template, result)
                return

            self.owner.__setattr__(self.property, self.type_converter(result))
            if hasattr(self, "entity_ha_update"):
                self.entity_ha_update()


    @callback
    def async_remove(self) -> None:
        if self.result_info:
            self.result_info.async_remove()
        self.entity._async_up = None
        self.entity_ha_update = None