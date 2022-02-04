## Notification bot for dvmn.org


### **Быстрый запуск**

Рекомендуемая версия интерпретатора Python 3.9+ [установите его](https://www.python.org) если ещё не сделали этого.

Перед запуском бота локально на своём компьютере или на сервере, которым вы можете управлять, то переименуйте файл .env.example в .env и заполните своими значениями

```dotenv
DVMN_TOKEN = PUT_DVMN_TOKEN_HERE
TG_TOKEN = PUT_TELEGRAM_TOKEN_HERE
TG_CHAT_ID = PUT_TELEGRAM_CHAT_ID_HERE
```

- **Примечание.** Если вы разворачиваете бот на хостинге, который не поддерживает создание или изменение конфигурационных файлов после деплоя (напр. Heroku) задайте переменные окружения с теми же названиями в настройках хостинга.

После этого установите необходимые пакеты и запустите скрипт

```commandline
$ python3 - m pip install -r requirements.txt
$ python3 main.py
```

### **Дополнительная информация**
Код создан в учебных целях в рамках учебного курса по созданию чат-ботов - [DVMN.org](https://dvmn.org)
