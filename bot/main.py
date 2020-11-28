import argparse
import asyncio
import functools
import logging
import os
import typing

import aiogram  # type: ignore
import aiogram.contrib.fsm_storage.memory  # type: ignore
import aiogram.dispatcher.filters.state  # type: ignore
import aiogram.dispatcher  # type: ignore

from . import context
from . import handlers


_PERIODIC_TASK_SLEEP_SECONDS = 10


def _parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument(
        '-c',
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file',
    )
    parse.add_argument(
        '-l', '--logfile', type=str, default=None, help='Path to log file',
    )
    args = parse.parse_args()
    return args


def _extract_chat_id(
        param: typing.Union[
            aiogram.types.Message, aiogram.types.CallbackQuery,
        ],
) -> int:
    if hasattr(param, 'chat'):
        return param.chat.id
    return param.message.chat.id


async def _not_authorized(
        ctx: context.Context,
        arg: typing.Union[aiogram.types.Message, aiogram.types.CallbackQuery],
):
    logging.info(
        'Not authorized. id: %s, name: "%s"',
        arg.from_user.id,
        arg.from_user.full_name,
    )

    await ctx.bot.send_message(
        arg.chat.id,
        'You aren\'t authorized. Did you forget to add your ID ({}) to config?'.format(
            arg.from_user.id,
        ),
    )


def _only_for_authorized(ctx: context.Context):
    def decorator(func):
        @functools.wraps(func)
        async def handle(
                arg: typing.Union[
                    aiogram.types.Message, aiogram.types.CallbackQuery,
                ],
                *args,
                **kwargs,
        ):
            if not ctx.authorizer.is_authorized(arg.from_user.id):
                await _not_authorized(ctx, arg)
                return

            return await func(arg, *args, **kwargs)

        return handle

    return decorator


def _verbose_handler(bot: aiogram.Bot):
    def decorator(func):
        async def _reply(arg, message):
            chat_id = _extract_chat_id(arg)
            await bot.send_message(chat_id, message)

        @functools.wraps(func)
        async def handle(
                arg: typing.Union[
                    aiogram.types.Message, aiogram.types.CallbackQuery,
                ],
                *args,
                **kwargs,
        ):
            try:
                await func(arg, *args, **kwargs)
            except BaseException as e:
                await _reply(arg, 'Something went wrong: ' + repr(e))
                raise

        return handle

    return decorator


async def _periodic_main(ctx: context.Context):
    while True:
        try:
            await asyncio.sleep(_PERIODIC_TASK_SLEEP_SECONDS)
            await handlers.periodic_update_status(ctx)
        except BaseException:
            logging.exception('Periodic task failed')


def _register_handlers(ctx: context.Context, dp: aiogram.Dispatcher):
    bot = ctx.bot

    def wrap_f(handler, auth_required):
        f = functools.partial(handler, ctx)
        f = _only_for_authorized(ctx)(f)
        return _verbose_handler(bot)(f)

    def register_handler(handler, *args, auth_required=True, **kwargs):
        dp.register_message_handler(
            wrap_f(handler, auth_required), *args, **kwargs,
        )

    def register_kb_callback(handler, *args, auth_required=True, **kwargs):
        dp.register_callback_query_handler(
            wrap_f(handler, auth_required), *args, **kwargs,
        )

    register_handler(handlers.start, commands=['start'])
    register_handler(handlers.server_ip, commands=['server_ip'])


def main():
    args = _parse_args()

    logging.basicConfig(
        filename=args.logfile,
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    ctx = context.Context(args.config, os.environ)

    dp = aiogram.Dispatcher(ctx.bot)
    _register_handlers(ctx, dp)

    ctx.aio_loop.create_task(_periodic_main(ctx))
    aiogram.executor.start_polling(dp, skip_updates=True)
