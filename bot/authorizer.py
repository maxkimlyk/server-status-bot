import datetime
import functools

from . import db


class Authorizer:
    def __init__(self, db_: db.Db, config: dict):
        self._db = db_
        self._telegram_user_id = int(config['telegram_user_id'])

    def is_authorized(self, telegram_user_id: int):
        return self._telegram_user_id == telegram_user_id
