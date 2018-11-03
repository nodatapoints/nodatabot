"""
Core Definitions for
Herbert and Herbert-
Submodules
"""

import inspect

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from hercurles_chat import *


with open('token.txt', 'r') as fobj:
    token = fobj.read().strip()

updater = Updater(token)


def register_bert(cls):
    """Adds a Bert to Herbert"""
    bot = cls()
    for _, method in inspect.getmembers(bot, inspect.ismethod):
        if hasattr(method, '_command_handler'):
            for command in method._commands:
                updater.dispatcher.add_handler(
                    method._command_handler(command, method)
                )

        elif hasattr(method, '_callback_query_handler'):
            updater.dispatcher.add_handler(
                method._callback_query_handler(method)
            )


def idle():
    updater.start_polling()
    updater.idle()


class BaseBert:
  """
  Common Submodule type
  """
  # TODO implementation

  def reply(self, *args, **kwargs):
      _t_reply_chunky(*args, **kwargs)
