"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import inspect
import logging

from telegram.ext import Updater


logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

with open('token.txt', 'r') as fobj:
    token = fobj.read().strip()

updater = Updater(token)

berts = []


def get_berts():
    return berts


def register_bert(cls):
    """Adds a Bert to Herbert"""
    bot = cls()
    berts.append(bot)
    for _, method in inspect.getmembers(bot, inspect.ismethod):
        if hasattr(method, 'command_handler'):
            for command in method.commands:
                updater.dispatcher.add_handler(
                    method.command_handler(command, method)
                )

        elif hasattr(method, 'callback_query_handler'):
            updater.dispatcher.add_handler(
                method.callback_query_handler(method)
            )


def idle():
    updater.start_polling()
    updater.idle()
