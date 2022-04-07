from typing import Any, Callable, Coroutine, Union

from homeassistant.core import HomeAssistant, callback


callable_type = Union[Callable[..., Any], Coroutine[Any, Any, Any]]


class Updatable:
    _on_update: Union[list[callable_type], None] = None

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

        
    def on_update(self, callable: callable_type) -> None:
        if not self._on_update:
            self._on_update = []
        self._on_update.append(callable)


    @callback
    def async_update(self):
        if self._on_update:
            for callable in self._on_update:
                self.hass.add_job(callable)


class Unloadable:
    _on_unload: Union[list[callable_type], None] = None
    
    def on_unload(self, callable: callable_type) -> None:
        if not self._on_unload:
            self._on_unload = []
        self._on_unload.append(callable)


    def unload(self):
        if self._on_unload:
            while self._on_unload:
                self._on_unload.pop()()