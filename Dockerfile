FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

USER root

RUN python -m pip install --upgrade pip
RUN pip install -r ./requirements.txt

COPY . .

CMD ["python", "./main.py"]