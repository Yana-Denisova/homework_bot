class UnavailableServerException(Exception):
    """Исключение, если не удалось получить ответ от API."""

    pass


class ResponseHomeworksNotInListException(Exception):
    """Исключение, если формат ответа API отличается от ожидаемого."""

    pass


class ResponseNoHomeworksException(Exception):
    """Исключение, если ответ API не содержит ключ homeworks."""

    pass


class TelegramError(Exception):
    """Исключение, если произошел при отправке сообщения в телеграмм."""

    pass
