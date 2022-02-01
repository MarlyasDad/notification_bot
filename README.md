## Notification bot for dvmn.org


### **Быстрый запуск**

Если у вас не установлен интерпретатор Python, [установите его](https://www.python.org).  
Рекомендуемая версия - Python 3.9+

Переименуйте файл config.example.ini в config.ini и заполните своими значениями

```ini
DVMN_TOKEN = PUT_DVMN_TOKEN_HERE
TG_TOKEN = PUT_TELEGRAM_TOKEN_HERE
TG_CHAT_ID = PUT_TELEGRAM_CHAT_ID_HERE
```

- Если вы разворачиваете бот на сервисе, который не поддерживает использование конфигурационных файлов (напр. Heroku), возможно использование переменных окружения с теми же названиями.

После этого установите необходимые пакеты и запустите скрипт

```commandline
$ python3 - m pip install -r requirements.txt
$ python3 main.py
```

### **Дополнительная информация**
Код создан в учебных целях в рамках учебного курса по созданию чат-ботов - [DVMN.org](https://dvmn.org)