

from ..const import (
    ATTR_ACTOR,
    ATTR_ACTOR_ACTION,
    ATTR_ACTOR_ENTITY,
    ATTR_ACTOR_ID,
    ATTR_ACTOR_TYPE,
    ATTR_DATA,
)

class ReactSignalDataReader():
    def __init__(self, event_variables: dict) -> None:
        self.variables = event_variables
        self.actor_data: dict = event_variables[ATTR_ACTOR][ATTR_DATA]

        self.actor_entity = self.actor_data.get(ATTR_ACTOR_ENTITY, None)
        self.actor_type = self.actor_data.get(ATTR_ACTOR_TYPE, None)
        self.actor_action = self.actor_data.get(ATTR_ACTOR_ACTION, None)
        self.actor_id = self.actor_data.get(ATTR_ACTOR_ID, None)