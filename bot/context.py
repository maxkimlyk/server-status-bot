import asyncio
from typing import Dict

import aiogram  # type: ignore

from . import authorizer
from . import config
from . import db
from . import http_client

class Context:
    def __init__(self, config_path: str, environ: Dict[str, str]):
        self.config = config.load_config(config_path, environ)
        self.db = db.Db(self.config['db_path_inside_container'])
        self.authorizer = authorizer.Authorizer(self.db, self.config)
        self.http_client = http_client.HttpClient(self.config)

        self.aio_loop = asyncio.get_event_loop()
        self.bot = aiogram.Bot(
            token=self.config['telegram_api_token'], loop=self.aio_loop)

        print(self.config['telegram_api_token'])
