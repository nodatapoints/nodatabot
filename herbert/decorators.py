"""
Define all the decorators!
"""

from functools import wraps

from telegram.ext import CommandHandler, CallbackQueryHandler

from basebert import Herberror

__all__ = ['command', 'aliases', 'callback']


def handle_herberrors(method):
    """
    Catches `Herberror` and sends the argument of the exception as a message
    to the user. When an exception of any other type is catched, it will send
    a default error message to the user and raise it again.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)

        except Herberror as error:
            self.send_message(*error.args)

        except Exception as e:
            self.send_message('Oops, something went wrong! 😱')
            raise e

    return wrapped


def pull_bot_and_update(bound_method, pass_update=False, pass_query=True):
    """
    Updates `bot` and `update` of the bot instance of the
    bound method before calling it.
    """
    # Honestly, this is extremely bodgy ... sad kamal
    @wraps(bound_method)
    def wrapped(bot, update, *args, **kwargs):
        bound_method.__self__.bot = bot
        bound_method.__self__.update = update
        if pass_query:
            args = (update.callback_query, ) + args

        if pass_update:
            args = (update, ) + args

        return bound_method(*args, **kwargs)

    return wrapped


def command(arg=None, *, pass_args=True, pass_update=False, **kwargs):
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
            callback = pull_bot_and_update(
                bound_method,
                pass_update,
                pass_query=False
            )
            return CommandHandler(name, callback, pass_args=pass_args, **kwargs)

        method._command_handler = handler
        method._commands = [method.__name__]
        return handle_herberrors(method)

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


def callback(arg=None, *, pass_update=False, pass_query=True, **kwargs):
    def callback_decorator(method):
        def handler(bound_method):
            callback = pull_bot_and_update(bound_method, pass_update, pass_query)
            return CallbackQueryHandler(callback, **kwargs)

        method._callback_query_handler = handler
        return handle_herberrors(method)

    if callable(arg):
        return callback_decorator(arg)

    return callback_decorator
