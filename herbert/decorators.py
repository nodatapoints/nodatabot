"""
Define all the decorators!
"""

from functools import wraps
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from herbert_utils import *

__all__ = ['command', 'aliases', 'callback']


def command(arg=None, pass_args=True, **kwargs):
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
            return CommandHandler(name, bound_method, pass_args=pass_args, **kwargs)

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


def callback(arg=None, **kwargs):

    def callback_decorator(method):

        def handler(bound_method):
            return CallbackQueryHandler(bound_method, **kwargs)

        method._callback_query_handler = handler
        return method

    if callable(arg):
        return callback_decorator(arg)

    return callback_decorator


