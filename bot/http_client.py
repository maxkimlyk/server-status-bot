import typing

import aiohttp


class HttpClient:
    def __init__(self, config: dict):
        self.session = aiohttp.ClientSession()
        self.timeout = config['http_timeout_seconds']

    async def get(
            self, url: str, headers: typing.Optional[dict] = None,
    ) -> str:
        async with self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                skip_auto_headers=None,
        ) as response:
            response.raise_for_status()
            return await response.text()

    async def destruct(self):
        await self.session.close()
