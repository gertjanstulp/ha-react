import attr

from homeassistant.core import Event, HomeAssistant

from . import config as co

class BaseEvent:
    def __init__(self, actor: str, actor_type: str, actor_action: str):
        self._actor = actor
        self._actor_type = actor_type
        self._actor_action = actor_action

    @property
    def actor(self):
        return self._actor

    @property
    def actor_type(self):
        return self._actor_type

    @property
    def actor_action(self):
        return self._actor_action

class BinarySensorEvent(BaseEvent):
    def __init__(self, event: Event):
        self.entity_id = event.data.get('entity_id', '')
        old_state = event.data.get('old_state', '')
        self.old_state = old_state.state if old_state else ''
        new_state = event.data.get('new_state')
        self.new_state = new_state.state if new_state else ''

        super().__init__(self.entity_id, 'binary_sensor', self.new_state)

class ActionEvent(BaseEvent):
    def __init__(self, actor: str, actor_type: str, actor_action: str):
        super().__init__(actor, actor_type, actor_action)
