
from ..const import (
    ATTR_ACTOR,
    ATTR_ACTOR_ACTION,
    ATTR_ACTOR_DATA,
    ATTR_ACTOR_ENTITY,
    ATTR_ACTOR_ID,
    ATTR_ACTOR_TYPE,
    ATTR_DATA,
)

class ReactSignalDataReader():
    
    def __init__(self, event_variables: dict) -> None:
        self.variables = event_variables
        data: dict = event_variables[ATTR_ACTOR][ATTR_DATA]

        self.actor_entity = data.get(ATTR_ACTOR_ENTITY, None)
        self.actor_type = data.get(ATTR_ACTOR_TYPE, None)
        self.actor_action = data.get(ATTR_ACTOR_ACTION, None)
        self.actor_id = data.get(ATTR_ACTOR_ID, None)
        self.actor_data = data.get(ATTR_ACTOR_DATA, None)