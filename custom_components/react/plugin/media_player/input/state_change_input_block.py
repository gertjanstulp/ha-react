from homeassistant.components.media_player import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.plugin.base import StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent, StateChangedEventPayload


class MediaPlayerStateData(StateChangeData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(event_payload)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class MediaPlayerStateChangeInputBlock(StateChangeInputBlock[MediaPlayerConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return MediaPlayerStateData(react_event.payload)
