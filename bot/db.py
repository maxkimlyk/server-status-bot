import datetime
from typing import Any, Dict
import json
import logging

import sqlite3

from . import exceptions


class Db:
    def __init__(self, path_to_dbfile):
        self._connection = sqlite3.connect(path_to_dbfile)

    def set_value(self, key: str, value: str):
        self._connection.execute(
            'INSERT OR REPLACE INTO keyvalue(key, value) ' 'VALUES (?, ?)',
            (key, value),
        )
        self._connection.commit()

    def get_value(self, key: str) -> str:
        row = self._connection.execute(
            'SELECT value FROM keyvalue ' 'WHERE key = ?', (key,),
        ).fetchone()

        if row is None:
            raise exceptions.NoData('no value at key "{}"'.format(key))

        return row[0]

    def set_json_value(self, key, value: Dict[str, Any]):
        self.set_value(key, json.dumps(value))

    def get_json_value(self, key) -> Dict[str, Any]:
        str_value = self.get_value(key)
        return json.loads(str_value)
