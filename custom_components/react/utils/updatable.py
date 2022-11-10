from typing import Any, Callable, Coroutine, Union

from homeassistant.core import callback, HomeAssistant

callable_type = Union[Callable[..., Any], Coroutine[Any, Any, Any]]


class Updatable:
    
    def __init__(self, hass: HomeAssistant) -> None:
        self._on_update: Union[list[callable_type], None] = []
        self._hass = hass

        
    def on_update(self, callable: callable_type) -> None:
        if not self._on_update:
            self._on_update = []
        self._on_update.append(callable)


    @callback
    def async_update(self, *args) -> None:
        if self._on_update:
            for callable in self._on_update:
                self._hass.add_job(callable, *args)

    
    def destroy(self) -> None:
        self._on_update.clear()
