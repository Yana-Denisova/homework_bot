class UnavailableServerException(Exception):
    """Исключение, если не удалось получить ответ от API."""

    pass


class ResponseNoHomeworksException(Exception):
    """Исключение, если ответ API не содержит ключ homeworks."""

    pass


class TelegramError(Exception):
    """Исключение, если произошел при отправке сообщения в телеграмм."""

    pass


class RequestExceptionError(Exception):
    """исключение если URL практикума недоступен."""

    pass


class JSONDecodeErrorException(Exception):
    """Исключение, если json не порматируется."""

    pass
