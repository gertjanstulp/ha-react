from custom_components.react.utils.struct import DynamicData

ATTR_MESSAGE_DATA = "message_data"

NOTIFY_RESOLVER_KEY = "react_notify_resolver"


class FeedbackItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.title: str = None
        self.feedback: str = None
        self.acknowledgement: str = None

        self.load(source)