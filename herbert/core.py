"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import logging

from telegram.ext import Updater, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update

from common.herbert_utils import is_cmd_decorated
import path

__all__ = ['Herbert']

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


class Herbert:
    """
    Wrap ptb's Updater

    .register_bot() will add all handlers
    for all methods of a BaseBert-subclass

    The bot can then run with .idle()
    """

    def __init__(self, token_file='token.txt'):
        path.change_path()

        with open(token_file, 'r') as fobj:
            self.token = fobj.read().strip()

        self.updater = Updater(self.token)

    def register_bert(self, cls):
        """Adds a Bert to Herbert"""
        bot = cls()
        berts.append(bot)

        for method in bot.enumerate_members():
            if is_cmd_decorated(method):
                inf = method.cmdinfo
                for handler in inf.handlers(method):
                    self.updater.dispatcher.add_handler(handler)

                if inf.allow_inline:
                    inline_methods[method.__name__] = inf.invoke(method)
                    for command in inf.aliases:
                        inline_aliases[command] = method.__name__

            elif hasattr(method, 'callback_query_handler'):
                self.updater.dispatcher.add_handler(
                    method.callback_query_handler(method)
                )

        cmds = ", ".join((m.__name__ for m in bot.enumerate_cmds()))
        logging.getLogger('herbert.SETUP').debug("Registered Bert %s of type %s (%s)", bot, cls.__name__, cmds)

    def register_inline_handler(self):
        self.updater.dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

    def start(self):
        self.updater.start_polling()

    def idle(self):
        """ start the updater event loop """
        self.start()
        self.updater.idle()


def handle_inline_query(update: Update, context: CallbackContext, line=None):
    """
    If python-telegram-bot receives an inline query, this function
    will select the correct command handler based on the query string,
    then run the command with an appropriate context object to allow
    answering the query by using the normal send methods
    """
    query = None

    if line is not None:
        query = line
    elif update.inline_query is not None:
        query = update.inline_query.query
    else:
        raise ValueError("Handler called without valid query")

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
