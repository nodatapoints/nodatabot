import logging
from functools import wraps
import inspect

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

with open('token.txt', 'r') as fobj:
    token = fobj.read().strip()

updater = Updater(token)


class Herberror(Exception):
    '''Basic herbert error'''


def bot_proxy(handler):
    @wraps(handler)
    def wrapper(bot, update, *args, **kwargs):
        try:
            handler(bot, update, *args, **kwargs)

        except (Herberror, AssertionError) as error:
            bot.send_message(update.message.chat_id, *error.args)

        except Exception as e:
            bot.send_message(
                (update.message or update.callback_query.message).chat_id,
                'Oops, something went wrong! :P'
            )
            raise e

    return wrapper


def command(arg=None, **kwargs):
    """
    Generates a command decorator (see `command_decorator`).
    `**kwargs` will be passed to the dispatcher.
    When applied directly via `@command` it acts like the decorator it returns.

    """
    def command_decorator(method):
        """Adds an callable `handler` attribute to the method, which will return
        appropriate handler for the dispatcher.
        """
        # This is necessary because the method itself is called as
        # `cls.method(self, *args)`, but the callback wants the bound method
        # that only takes `*args`. The bound method can only be constructed
        # with the actual instance, which is only known to `Herbert`.
        if not callable(method):
            raise ValueError(f'{method} not callable. Did you use @command()?')

        def handler(name, bound_method):
            return CommandHandler(name, bound_method, **kwargs)

        method._command_handler = handler
        method._commands = [method.__name__]
        return method

    if callable(arg):
        return command_decorator(arg)

    return command_decorator


def aliases(*args):
    def decorator(method):
        try:
            method._commands.extend(args)
            return method

        except AttributeError:
            raise ValueError('Only command-decorated methods an have aliases')

    return decorator


def callback(method):
    def handler(bound_method):
        # same stuff like `command_decorator`
        return CallbackQueryHandler(bound_method)

    method._callback_query_handler = handler
    return method


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
