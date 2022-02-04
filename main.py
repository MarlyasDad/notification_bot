import os
from typing import List
from time import sleep
import requests
from dataclasses import dataclass
import logging
import telegram
from dotenv import load_dotenv


@dataclass
class BotConfig:
    dvmn_token: str
    tg_token: str
    tg_chat_id: str


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
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logger(tg_bot: telegram.bot.Bot, chat_id: str):
    new_logger = logging.getLogger()
    new_logger.setLevel(logging.INFO)
    new_logger.addHandler(TelegramLogsHandler(tg_bot, chat_id))
    return new_logger


def setup_configs() -> BotConfig:
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    return BotConfig(
        dvmn_token=os.environ.get("DVMN_TOKEN"),
        tg_token=os.environ.get("TG_TOKEN"),
        tg_chat_id=os.environ.get("TG_CHAT_ID"),
    )


def dvmn_poller(logger: logging.Logger, tg_bot: telegram.bot.Bot,
                configs: BotConfig):
    long_poll_url = "https://dvmn.org/api/long_polling/"
    status_texts = {
        "success": "Преподавателю всё понравилось, можно приступать "
                   "к следующему уроку!\n",
        "failure": "К сожалению, в работе нашлись ошибки.\n"
    }
    headers = {
        "Authorization": f"Token {configs.dvmn_token}"
    }
    payload = {}

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
                tg_bot.send_message(chat_id=configs.tg_chat_id, text=message)
        else:
            attempts = LongPollingTimeout(**dvmn_new_attempts)
            payload["timestamp"] = attempts.timestamp_to_request


def main():
    configs: BotConfig = setup_configs()

    tg_bot = telegram.Bot(token=configs.tg_token)
    logger = setup_logger(tg_bot, configs.tg_chat_id)

    logger.info("Бот запущен")
    try:
        dvmn_poller(logger, tg_bot, configs)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    main()
