from typing import Any, Awaitable, Callable, Union

from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.core import Event, HomeAssistant

from .. import const as co


class Dispatcher:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.signal_disconnects = []
        self.event_disconnects = []
        self.tagged_disconnects = {}


    def connect_signal(self, signal: str, target: Callable[..., Any]) -> None:
        self.signal_disconnects.append(async_dispatcher_connect(self.hass, signal, target))


    def send_signal(self, signal: str, *args: Any) -> None:
        async_dispatcher_send(self.hass, signal, *args)


    def connect_event(self, event: str, callable: Callable[[Event], Union[None, Awaitable[None]]], filter: Union[Callable[[Event], bool], None] = None, tag: str = None):
        disconnect = self.hass.bus.async_listen(event, callable, filter)
        if tag:
            if not tag in self.tagged_disconnects:
                self.tagged_disconnects[tag] = []
            self.tagged_disconnects[tag].append(disconnect)
        else:
            self.event_disconnects.append(disconnect)


    def send_event(self, event: str, event_data: dict):
        self.hass.bus.async_fire(event, event_data)


    def stop_tag(self, tag: str):
        if tag in self.tagged_disconnects:
            for disconnect in self.tagged_disconnects.pop(tag):
                disconnect()

    def stop(self) -> None:
        for disconnect in self.signal_disconnects:
            disconnect()
        for disconnect in self.event_disconnects:
            disconnect()
        for tag in self.tagged_disconnects:
            for disconnect in self.tagged_disconnects[tag]:
                disconnect()

        self.signal_disconnects = []
        self.event_disconnects = []
        self.tagged_disconnects = {}


def get(hass: HomeAssistant) -> Dispatcher:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].dispatcher
    return None
