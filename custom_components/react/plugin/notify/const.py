from custom_components.react.utils.struct import DynamicData

PLUGIN_NAME = "notify"
ATTR_MESSAGE_DATA = "message_data"
CONFIG_DEFAULT_SERVICE_TYPE = "default_service_type"


class FeedbackItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.title: str = None
        self.feedback: str = None
        self.acknowledgement: str = None

        self.load(source)