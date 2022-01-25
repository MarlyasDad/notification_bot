## Notification bot for dvmn.org


### **Быстрый запуск**

Если у вас не установлен интерпретатор Python, [установите его](https://www.python.org).  
Рекомендуемая версия - Python 3.9+

Переименуйте файл config.example.ini в config.ini и заполните своими значениями

```ini
DEVMAN_TOKEN = PUT_DVMN_TOKEN_HERE
TELEGRAM_TOKEN = PUT_TELEGRAM_TOKEN_HERE
CHAT_ID = PUT_CHAT_ID_HERE
```

После этого установите необходимые пакеты и запустите скрипт

```commandline
$ python3 - m pip install -r requirements.txt
$ python3 min.py
```

### **Дополнительная информация**
Код создан в учебных целях. В рамках учебного курса по веб-разработке - [DVMN.org](https://dvmn.org)