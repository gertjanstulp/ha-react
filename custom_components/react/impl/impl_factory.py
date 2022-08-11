
from importlib import import_module
from pathlib import Path

from ..utils.events import NotifyFeedbackEventDataReader
from ..base import ReactBase


class ImplFactory:
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.impls = {}
        

    async def async_get_notify_provider(self):
        provider = self.impls.get("notify")
        if not provider:
            provider_name = self.react.configuration.impl_config.notify
            if provider_name:
                # impl_path = Path(__file__).parent
                provider_name = (f"{__package__}.{provider_name}.notify_provider")
                provider_module = import_module(provider_name)
                provider = await provider_module.async_setup_provider(react=self.react)
            self.impls["notify"] = provider
        return provider


class NotifyProvider:
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    def get_reader_type(self):
        raise NotImplementedError()


    @property
    def feedback_event(self):
        raise NotImplementedError()


    async def async_send_feedback(self, event_reader: NotifyFeedbackEventDataReader):
        raise NotImplementedError()
