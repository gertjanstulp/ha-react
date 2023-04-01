from homeassistant.core import Context

from custom_components.react.base import ReactBase


class MediaPlayerService():
    def __init__(self, react: ReactBase) -> None:
        self.react = react

    
    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        raise NotImplementedError()