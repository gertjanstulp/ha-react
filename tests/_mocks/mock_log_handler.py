from logging import  Handler


class MockLogHandler(Handler):
    def __init__(self )-> None:
        self.records: list = list()
        Handler.__init__(self=self)


    def emit(self, record) -> None:
        self.records.append(record)

    def has_record(self, level_name: str, message: str):
        matches = [ item for item in self.records if item.levelname == level_name and item.msg == message ]
        return len(matches) > 0