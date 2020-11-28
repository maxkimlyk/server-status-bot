from . import http_client
from . import context

_URL = 'http://ifconfig.me'
_USER_AGENT = 'curl/7.54'


async def get(ctx: context.Context) -> str:
    ip = await ctx.http_client.get(
        _URL, {'User-Agent': _USER_AGENT},
    )

    return ip

