"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import inspect
import logging
import path


from telegram.ext import Updater, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update

from common.herbert_utils import is_cmd_decorated

logging.basicConfig(
    style='{',
    datefmt='%d.%m. %H:%M:%S',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

berts = []
inline_methods = {}
inline_aliases = {}


def init():
    global updater, token

    path.change_path()

    with open('token.txt', 'r') as fobj:
        token = fobj.read().strip()

    updater = Updater(token)


def register_bert(cls):
    """Adds a Bert to Herbert"""
    bot = cls()
    berts.append(bot)

    for method in bot.enumerate_members():
        if is_cmd_decorated(method):
            inf = method.cmdinfo
            for handler in inf.handlers(method):
                updater.dispatcher.add_handler(handler)

            if inf.allow_inline:
                inline_methods[method.__name__] = inf._invoke(method)
                for command in inf.aliases:
                    inline_aliases[command] = method.__name__

        elif hasattr(method, 'callback_query_handler'):
            updater.dispatcher.add_handler(
                method.callback_query_handler(method)
            )

    cmds = ", ".join((m.__name__ for m in bot.enumerate_cmds()))
    logging.getLogger('herbert.SETUP').debug(f"Registered Bert {bot} of type {cls.__name__} ({cmds})")


def handle_inline_query(update: Update, context: CallbackContext, line=None):
    bot = context.bot
    query = line or update.inline_query.query

    command, *args = query.split(" ")

    for alias, name in inline_aliases.items():
        if command == alias:
            inline_methods[name](
                update,
                context,
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
