from typing import Any, Callable, Coroutine, Union

from homeassistant.core import callback

from ..base import ReactBase

callable_type = Union[Callable[..., Any], Coroutine[Any, Any, Any]]


class Updatable:
    def __init__(self, react: ReactBase) -> None:
        self._on_update: Union[list[callable_type], None] = []
        self._react = react

        
    def on_update(self, callable: callable_type) -> None:
        if not self._on_update:
            self._on_update = []
        self._on_update.append(callable)


    @callback
    def async_update(self):
        if self._on_update:
            for callable in self._on_update:
                self._react.hass.add_job(callable,)

    
    def destroy(self):
        del self._on_update
