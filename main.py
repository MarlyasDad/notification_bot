from typing import List
from time import sleep
import requests
from dataclasses import dataclass
import configparser
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


config = configparser.ConfigParser()
config.read('config.ini')

DEVMAN_TOKEN = config["notification_bot"].get("DEVMAN_TOKEN")
TELEGRAM_TOKEN = config["notification_bot"].get("TELEGRAM_TOKEN")
CHAT_ID = config["notification_bot"].get("CHAT_ID")

SUCCESS_MESSAGE = "Преподавателю всё понравилось, можно приступать" \
                  " к следующему уроку!\n"
FAILURE_MESSAGE = "К сожалению, в работе нашлись ошибки.\n"


LONG_POLL_URL = "https://dvmn.org/api/long_polling/"

headers = {
    "Authorization": f"Token {DEVMAN_TOKEN}"
}

payload = {}


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = requests.get(LONG_POLL_URL, headers=headers,
                                    params=payload, timeout=95)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(30)
            continue

        response_loads = response.json()

        if response_loads.get("status") == "found":
            long_response = LongPollingFound(**response_loads)
            long_timestamp = long_response.last_attempt_timestamp
            for attempt in long_response.new_attempts:
                if attempt.get("is_negative"):
                    task_status = FAILURE_MESSAGE
                else:
                    task_status = SUCCESS_MESSAGE

                lesson_title = attempt.get('lesson_title')
                title = f"У вас проверили работу \"{lesson_title}\"\n\n"

                message = title + task_status + attempt.get("lesson_url")
                bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            long_response = LongPollingTimeout(**response_loads)
            long_timestamp = long_response.timestamp_to_request

        payload["timestamp"] = long_timestamp


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Бот был остановлен пользователем")
