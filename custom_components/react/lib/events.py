import attr

from homeassistant.core import HomeAssistant

from . import config as co

@attr.s(slots=True, frozen=False)
class ActionEvent:
    actor = attr.ib(type=str, default=None)
    actor_type = attr.ib(type=str, default=None)
    actor_action = attr.ib(type=str, default=None)

    def is_match(self, workflow: co.Workflow) -> bool:
        return (self.actor in workflow.actor and 
                self.actor_type == workflow.actor_type and 
                self.actor_action == workflow.actor_action)

# class EventSender:
#     def __init__(self, hass: HomeAssistant):
#         self._hass = hass
        
#     def send_event(self, reaction):
#         self._hass.bus.async_fire(co.EVENT_REACT_REACTION, attr.asdict(reaction, filter=lambda attr, value: attr.name not in ["reaction_timestamp"]))