#!/bin/bash

mkdir /var/cache/server-status-bot
sqlite3 /var/cache/server-status-bot/db.db < createdb.sql || exit 2

python run.py --config config.yaml
