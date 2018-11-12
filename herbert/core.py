"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import inspect
import logging

from telegram.ext import Updater, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent

logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

with open('token.txt', 'r') as fobj:
    token = fobj.read().strip()

updater = Updater(token)

berts = []
inline_methods = {}


def get_berts():
    return berts


def get_inline_methods():
    return inline_methods


def register_bert(cls):
    """Adds a Bert to Herbert"""
    bot = cls()
    berts.append(bot)

    for _, method in inspect.getmembers(bot, inspect.ismethod):
        if hasattr(method, 'inline'):
            if method.inline:
                inline_methods[method.__name__] = method.get_inner(method)

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

    for method in get_inline_methods():
        if command == method:
            get_inline_methods()[method](
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


updater.dispatcher.add_handler(InlineQueryHandler(handle_inline_query))


# ############# TEMP #############
def unknown_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="WTF do you mean?")


from telegram.ext import MessageHandler, Filters

updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))


# ########### END TEMP ###########


def idle():
    updater.start_polling()
    updater.idle()
