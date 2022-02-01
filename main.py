import os
from typing import List
from time import sleep
import requests
from dataclasses import dataclass
import configparser
import logging
import telegram


LONG_POLL_URL = "https://dvmn.org/api/long_polling/"
STATUS_TEXTS = {
    "success": "Преподавателю всё понравилось, можно приступать "
               "к следующему уроку!\n",
    "failure": "К сожалению, в работе нашлись ошибки.\n"
}


@dataclass
class LongPollingTimeout:
    status: str
    timestamp_to_request: float
    request_query: list


@dataclass
class LongPollingFound:
    status: str
    last_attempt_timestamp: float
    new_attempts: List[dict]
    request_query: list


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        print(log_entry)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logger(tg_bot: telegram.bot.Bot, chat_id: str):
    new_logger = logging.getLogger()
    new_logger.setLevel(logging.INFO)
    new_logger.addHandler(TelegramLogsHandler(tg_bot, chat_id))
    return new_logger


def set_config(name, config_file):
    try:
        config_value = config_file["notification_bot"].get(name)
    except KeyError:
        config_value = os.environ.get(name)
    return config_value


def main(tg_bot: telegram.bot.Bot, status_texts: dict, long_poll_url: str,
         dvmn_token: str, tg_chat_id: str):
    payload = {}

    headers = {
        "Authorization": f"Token {dvmn_token}"
    }
    logger.info("Бот запущен")

    while True:
        try:
            response = requests.get(long_poll_url, headers=headers,
                                    params=payload, timeout=95)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            logger.warning(f"Таймаут соединения с {long_poll_url}")
            sleep(30)
            continue
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ошибка соединения с {long_poll_url}")
            sleep(30)
            continue
        except requests.exceptions.HTTPError as ex:
            logger.warning(f"Сервер ответил ошибкой {ex}")
            sleep(30)
            continue

        dvmn_new_attempts: dict = response.json()

        if dvmn_new_attempts.get("status") == "found":
            attempts = LongPollingFound(**dvmn_new_attempts)
            payload["timestamp"] = attempts.last_attempt_timestamp
            for attempt in attempts.new_attempts:
                if attempt.get("is_negative"):
                    task_status = status_texts["failure"]
                else:
                    task_status = status_texts["success"]

                lesson_title = attempt.get('lesson_title')
                title = f"У вас проверили работу \"{lesson_title}\"\n\n"

                message = f"{title}{task_status}{attempt.get('lesson_url')}"
                tg_bot.send_message(chat_id=tg_chat_id, text=message)
        else:
            attempts = LongPollingTimeout(**dvmn_new_attempts)
            payload["timestamp"] = attempts.timestamp_to_request


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    DVMN_TOKEN = set_config("DVMN_TOKEN", config)
    TG_TOKEN = set_config("TG_TOKEN", config)
    TG_CHAT_ID = set_config("TG_CHAT_ID", config)

    bot = telegram.Bot(token=TG_TOKEN)
    logger = setup_logger(bot, TG_CHAT_ID)

    try:
        main(bot, STATUS_TEXTS, LONG_POLL_URL, DVMN_TOKEN, TG_CHAT_ID)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
