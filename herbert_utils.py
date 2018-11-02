import logging
from functools import wraps
from contextlib import redirect_stdout

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


__all__ = [
    'Herberror',
    'bot_proxy',
    'command_handler',
    'callback_handler',
    'idle',
    'logging',
]

with open('token.txt', 'r') as fobj:
    token = fobj.read().strip()

updater = Updater(token)

logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)


class Herberror(Exception):
    '''Basic herbert error'''


class BufferBotWrapper:
    def __init__(self, bot, update):
        self.bot = bot
        self.chat_id = update.message.chat_id

    def write(self, message):
        if message != '\n':
            self.bot.send_message(self.chat_id, message)


def bot_proxy(handler):
    @wraps(handler)
    def wrapper(bot, update):
        try:
            wrapped_buffer = BufferBotWrapper(bot, update)
            with redirect_stdout(wrapped_buffer):
                handler(bot, update)

        except Herberror as error:
            bot.send_message(update.message.chat_id, *error.args)

    return wrapper


def command_handler(command, **kwargs):
    def decorator(handler):
        updater.dispatcher.add_handler(
            CommandHandler(command, handler, **kwargs)
        )
        return handler

    return decorator


def callback_handler(command, **kwargs):
    def decorator(handler):
        updater.dispatcher.add_handler(
            CallbackQueryHandler(handler, **kwargs)
        )
        return handler

    return decorator


def idle():
    updater.start_polling()
    updater.idle()
