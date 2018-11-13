"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import inspect
import logging
import path

from telegram.ext import Updater, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent

logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

berts = []
inline_methods = {}
inline_aliases = {}


def init():
    global updater, token

    path.change_path()

    with open('token.txt', 'r') as fobj:
        token = fobj.read().strip()

    updater = Updater(token)


def get_berts():
    return berts


def get_inline_methods():
    return inline_methods


def get_inline_aliases():
    return inline_aliases


def register_bert(cls):
    """Adds a Bert to Herbert"""
    bot = cls()
    berts.append(bot)

    for _, method in inspect.getmembers(bot, inspect.ismethod):
        if hasattr(method, 'inline'):
            if method.inline:
                inline_methods[method.__name__] = method.get_inner(method)
                for command in method.commands:
                    inline_aliases[command] = method.__name__

        if hasattr(method, 'command_handler'):
            for command in method.commands:
                updater.dispatcher.add_handler(
                    method.command_handler(command, method)
                )

        elif hasattr(method, 'callback_query_handler'):
            updater.dispatcher.add_handler(
                method.callback_query_handler(method)
            )


def handle_inline_query(bot, update, line=None):
    query = line or update.inline_query.query

    command, *args = query.split(" ")

    for alias, name in get_inline_aliases().items():
        if command == alias:
            get_inline_methods()[name](
                bot,
                update,
                inline=True,
                inline_query=update.inline_query,
                inline_args=args
            )

            return True

    update.inline_query.answer([
        InlineQueryResultArticle(
            id="error0",
            title='Failed to find Command "' + command + '".',
            input_message_content=InputTextMessageContent("Hello, guys!")
        )
    ])

    return False


def register_inline_handler():
    updater.dispatcher.add_handler(InlineQueryHandler(handle_inline_query))


def idle():
    updater.start_polling()
    updater.idle()
