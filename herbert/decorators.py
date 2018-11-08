"""
Define all the decorators!
"""

from functools import wraps

from telegram.ext import CommandHandler, CallbackQueryHandler

from basebert import Herberror

__all__ = ['pull_string', 'handle_herberrors', 'pull_bot_and_update', 'command', 'aliases', 'callback']


def pull_string(text):
    _, _, string = text.partition(' ')
    return string


def handle_herberrors(method):
    """
    Catches `Herberror` and sends the argument of the exception as a message
    to the user. When an exception of any other type is caught, it will send
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


def pull_bot_and_update(bound_method, pass_update=False, pass_query=True,
                        pass_string=False):
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

        if pass_string:
            string = pull_string(bound_method.__self__.message.text)
            args = (string, ) + args

        return bound_method(*args, **kwargs)

    return wrapped


def command(arg=None, *, pass_args=None, pass_update=False,
            pass_string=False, **kwargs):
    """
    Generates a command decorator (see `command_decorator`).
    `**kwargs` will be passed to the dispatcher.
    When applied directly via `@command` it acts like the decorator it returns.
    `pass_args: bool`
        Hands the decorated handler a tuple of the individual arguments of the
        command message

    `pass_update: bool`
        Will pass the `telegram.Update` object of the message to the handler
        as an argument.

    `pass_string: bool`
        Will pass the handler the original message string without the command and
        the following whitespace.
        Note that this will overwrite `pass_args` to `False`, unless explicitly
        specified otherwise.
    """
    if pass_args is None:
        pass_args = False if pass_string else True

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
                pass_update=pass_update,
                pass_query=False,
                pass_string=pass_string
            )
            return CommandHandler(
                name, callback, pass_args=pass_args, **kwargs)

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
            callback = pull_bot_and_update(
                bound_method, pass_update, pass_query)
            return CallbackQueryHandler(callback, **kwargs)

        method._callback_query_handler = handler
        return handle_herberrors(method)

    if callable(arg):
        return callback_decorator(arg)

    return callback_decorator
