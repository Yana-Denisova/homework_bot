import logging
import os
import time
import sys
import json
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (ResponseNoHomeworksException, TelegramError,
                        UnavailableServerException)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

FORMAT = '%(asctime)s, %(levelname)s, %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения в TELEGRAM."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение:"{message}" успешно отправлено')
    except TelegramError as error:
        logger.error(f'Сбой: {error} при отправке'
                     f'сообщения:"{message}" в телеграмм')
        raise TelegramError(f'Сбой: {error} при отправке'
                            f'сообщения:"{message}" в телеграмм')


def get_api_answer(current_timestamp):
    """Получение ответа от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(url=ENDPOINT,
                                         headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        logger.error(f'URL практикума недоступен: {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise UnavailableServerException(
            f'Сервер API недоступен: {homework_statuses.status_code}'
        )
    try:
        homework_statuses.json()
    except json.decoder.JSONDecodeError as error:
        logger.error(f'Ошибка форматирования json: {error}')
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        raise TypeError(
            'Формат ответа API отличается от ожидаемого'
        )
    if not isinstance(response['homeworks'], list):
        raise KeyError(
            'Формат ответа API отличается от ожидаемого'
        )
    if response['homeworks'] is None:
        raise ResponseNoHomeworksException(
            'Ответ API не содержит ключ homeworks')
    if len(response.get('homeworks')) != 0:
        return response.get('homeworks')
    else:
        raise ResponseNoHomeworksException(
            'Домашка пока не взята на проверку')


def parse_status(homework):
    """Проверка статуса  домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В словаре homeworks нет ключа homework_name')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError('Неизвестный статус')
    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия необходимых токенов для работы бота."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logger.critical('Отсутствуют необходимые токены!')
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    if check_tokens():
        while True:
            try:
                response = get_api_answer(current_timestamp)
                homework = check_response(response)
                if homework != []:
                    send_message(bot, parse_status(homework[0]))
                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            else:
                logger.debug('Отсутствие в ответе новых статусов.')
                time.sleep(RETRY_TIME)
    else:
        sys.exit('Завершение работы программы '
                 'из-за отсутствия необходимых токенов.')


if __name__ == '__main__':
    main()
