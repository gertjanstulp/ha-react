from logging import Logger


class LogManager:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger


    def info(self, category: str, message: str, *args) -> None:
        self.logger.info(self.format_message(category, message.format(*args)))


    def warn(self, category: str, message: str, *args) -> None:
        self.logger.warn(self.format_message(category, message.format(*args)))


    def error(self, category: str, message: str, *args) -> None:
        self.logger.error(self.format_message(category, message.format(*args)))


    def format_message(self, category: str, message: str) -> str:
        category_formatted = "{}:".format(category)
        return "{} {}".format(category_formatted, message)


    def format_data(self, id: str = None, entity: str = None, type: str = None, action: str = None, overwrite: bool = None):
        items = []

        if id: items.append("id='{}'".format(id))
        if entity: items.append("entity='{}'".format(entity))
        if type: items.append("type='{}'".format(type))
        if action: items.append("action='{}'".format(action))
        if overwrite: items.append("overwrite='{}'".format(overwrite))

        result = "|{}|".format("|".join(items)) 
        return result