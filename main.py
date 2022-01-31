from typing import List
from time import sleep
import requests
from dataclasses import dataclass
import configparser
import logging
import telegram


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


logging.basicConfig(
    format="[%(asctime)s] %(filename)s[LINE:%(lineno)d]# %(levelname)-8s "
           "%(message)s",
    filename="bot_log.txt",
    level=logging.INFO
)
logger = logging.getLogger(__file__)

config = configparser.ConfigParser()
config.read('config.ini')

DVMN_TOKEN = config["notification_bot"].get("DVMN_TOKEN")
TG_TOKEN = config["notification_bot"].get("TG_TOKEN")
TG_CHAT_ID = config["notification_bot"].get("TG_CHAT_ID")

SUCCESS_MESSAGE = "Преподавателю всё понравилось, можно приступать" \
                  " к следующему уроку!\n"
FAILURE_MESSAGE = "К сожалению, в работе нашлись ошибки.\n"


LONG_POLL_URL = "https://dvmn.org/api/long_polling/"

headers = {
    "Authorization": f"Token {DVMN_TOKEN}"
}

payload = {}


def main():
    bot = telegram.Bot(token=TG_TOKEN)

    while True:
        try:
            response = requests.get(LONG_POLL_URL, headers=headers,
                                    params=payload, timeout=95)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(30)
            continue
        except requests.exceptions.HTTPError as ex:
            logger.warning(ex)
            sleep(30)
            continue

        dvmn_new_attempts: dict = response.json()

        if dvmn_new_attempts.get("status") == "found":
            attempts = LongPollingFound(**dvmn_new_attempts)
            payload["timestamp"] = attempts.last_attempt_timestamp
            for attempt in attempts.new_attempts:
                if attempt.get("is_negative"):
                    task_status = FAILURE_MESSAGE
                else:
                    task_status = SUCCESS_MESSAGE

                lesson_title = attempt.get('lesson_title')
                title = f"У вас проверили работу \"{lesson_title}\"\n\n"

                message = f"{title}{task_status}{attempt.get('lesson_url')}"
                bot.send_message(chat_id=TG_CHAT_ID, text=message)
        else:
            attempts = LongPollingTimeout(**dvmn_new_attempts)
            payload["timestamp"] = attempts.timestamp_to_request


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Бот был остановлен пользователем")
