from __future__ import annotations

from dataclasses import dataclass

from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_REACTOR_ID, 
    ATTR_TYPE
)


@dataclass
class ReactionData:
    reactor_id: str
    entity: str
    type: str
    action: str
    data: dict
    session_id: int
    
    def to_trace_result(self):
        result = {
            ATTR_REACTOR_ID: self.reactor_id,
            ATTR_ENTITY: self.entity,
            ATTR_TYPE: self.type,
            ATTR_ACTION: self.action,
        }
        if self.data:
            result[ATTR_DATA] = self.data
        return result