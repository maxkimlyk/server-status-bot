import datetime
import logging
from typing import Tuple

import aiogram  # type: ignore

from . import context
from . import ip_getter
from . import types
from . import views

_CURRENT_MESSAGE_DB_KEY = 'current_message'
_STATUS_LAST_UPDATE_DB_KEY = 'status_last_update'

_UPDATE_PERIOD = datetime.timedelta(minutes=10)


async def start(ctx: context.Context, message: aiogram.types.Message):
    logging.info('Handling ' + message.text)
    status = await _get_status(ctx)
    response, parse_mode = views.status.build_response(status, ctx.config)
    sent_message = await ctx.bot.send_message(
        message.chat.id, response, parse_mode=parse_mode,
    )

    message_descr = {
        'chat_id': sent_message.chat.id,
        'message_id': sent_message.message_id,
    }

    ctx.db.set_json_value(_CURRENT_MESSAGE_DB_KEY, message_descr)


async def server_ip(ctx: context.Context, message: aiogram.types.Message):
    ip = await ip_getter.get(ctx)
    logging.info('Got ip: ', ip)
    await ctx.bot.send_message(message.chat.id, ip)


def _get_last_update_time(ctx: context.Context) -> datetime.datetime:
    try:
        value = ctx.db.get_value(_STATUS_LAST_UPDATE_DB_KEY)
        return datetime.datetime.fromisoformat(value)
    except BaseException as e:
        logging.info('Failed to get last update time: %s', repr(e))
        return datetime.datetime.min


async def _get_status(ctx: context.Context) -> types.Status:
    ip = await ip_getter.get(ctx)
    now = datetime.datetime.now()
    return types.Status(ip, now)

async def _update_status_message(ctx: context.Context):
    message_descr = ctx.db.get_json_value(_CURRENT_MESSAGE_DB_KEY)
    status = await _get_status(ctx)
    response, parse_mode = views.status.build_response(status, ctx.config)
    logging.info('Updating status: %s', status)
    await ctx.bot.edit_message_text(
        response,
        message_descr['chat_id'],
        message_descr['message_id'],
        parse_mode=parse_mode,
    )


async def periodic_update_status(ctx: context.Context):
    last_update_time = _get_last_update_time(ctx)
    now = datetime.datetime.now()

    if now < last_update_time or now - last_update_time >= _UPDATE_PERIOD:
        logging.info('Trying to update status due to period')
        await _update_status_message(ctx)
        ctx.db.set_value(_STATUS_LAST_UPDATE_DB_KEY, now.isoformat())
