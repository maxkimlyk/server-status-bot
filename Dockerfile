FROM python:3.8

WORKDIR /home
COPY requirements.txt ./

RUN pip install -r requirements.txt && \
    apt-get update && \
    apt-get install -y sqlite3

COPY *.py ./
COPY bot ./bot
COPY createdb.sql ./
COPY config.yaml ./

RUN mkdir /var/cache/system-status-bot
RUN sqlite3 /var/cache/system-status-bot/db.db < createdb.sql
ENTRYPOINT ["python", "run.py", "--config", "config.yaml"]
