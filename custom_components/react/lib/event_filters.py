from homeassistant.core import Event

from . import events as ev
from . import config as cf

class StateFilter:
    def __init__(self, entity_ids: list[str]):
        self.entity_ids = entity_ids

    def is_match(self, event: ev.BinarySensorEvent):
        return event.entity_id in self.entity_ids

class StateFilterForward(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: ev.BinarySensorEvent):
        return super().is_match(event)

class StateFilterToggle(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: ev.BinarySensorEvent):
        return (
            super().is_match(event) and
            event.old_state != event.new_state
        )

class StateFilterOn(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: ev.BinarySensorEvent):
        return (
            super().is_match(event) and
            event.old_state == 'off' and
            event.new_state == 'on'
        )

class StateFilterOff(StateFilter):
    def __init__(self, entity_ids: list[str]):
        super().__init__(entity_ids)

    def is_match(self, event: ev.BinarySensorEvent):
        return (
            super().is_match(event) and
            event.old_state == 'on' and
            event.new_state == 'off'
        )

class ActionEventFilter():
    def __init__(self, workflow: cf.Workflow):
        self._workflow = workflow

    def is_match(self, event: ev.ActionEvent) -> bool:
        if (event.actor in self._workflow.actor and event.actor_type == self._workflow.actor_type):
            if (self._workflow.action_forward):
                return True   
            else:
                return event.actor_action == self._workflow.actor_action
