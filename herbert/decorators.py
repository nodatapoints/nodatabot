"""
Define all the decorators!
"""

from functools import wraps
from datetime import datetime, timedelta
import logging

from telegram.ext import CommandHandler, CallbackQueryHandler
import telegram.error

from basebert import Herberror, BadHerberror
from common.constants import ERROR_FAILED, ERROR_PREFIX, BAD_ERROR_SUFFIX

__all__ = ['pull_string', 'handle_herberrors', 'pull_bot_and_update', 'command', 'aliases', 'callback']

reply_timeout = timedelta(seconds=30)


def pull_string(text):  # FIXME requires documentation
    _, _, string = text.partition(' ')
    return string


def handle_herberrors(method):
    """
    Returns a wrapper around `method`, which in turn
    Catches `Herberror` and sends the argument of the exception as a message
    to the user. When an exception of any other type is caught, it will send
    a default error message to the user and raise it again.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        """
        Functional wrapper to handle errors a command_handler
        might throw as well as errors that are entirely unexpected
        """
        try:
            return method(self, *args, **kwargs)

        except Herberror as e:
            res_text = " ".join([ERROR_PREFIX, *e.args])
            if isinstance(e, BadHerberror):
                res_text += BAD_ERROR_SUFFIX

            self.reply_text(res_text, parse_mode='HTML', disable_web_page_preview=True)
            msg, = e.args
            logging.debug(f'Herberror: "{msg}"')

        except telegram.error.TimedOut:
            logging.info('Timed out')

        except telegram.error.NetworkError:
            logging.info('Connection Failed')

        except Exception:
            self.reply_text(ERROR_FAILED)

            raise

    return wrapped


def pull_bot_and_update(bound_method, pass_update=False, pass_query=True,
                        pass_string=False, pass_args=False):
    """
    Returns a wrapper around bound_method, configured as per
    the **kwargs to this function. The wrapper will
    update `bot` and `update` of the bot instance of the
    bound method before calling it. It will also provide
    - an argument string, iff pass_string is true
    - an update-object, iff pass_update is true
    - a callback-query object, if such object exists and
        pass_query is true
    - an argument array, iff pass_args is true
    When the wrapper is called with inline=True, it will additionally
    provide access to the objects required to reply to an inline
    query.
    """
    @wraps(bound_method)
    def wrapped(bot, update, *args, inline=False, inline_query=None,
                inline_args=[], **kwargs):

        bound_method.__self__.bot = bot
        bound_method.__self__.update = update
        bound_method.__self__.inline = inline
        bound_method.__self__.inline_query = inline_query

        delta = datetime.now() - update.message.date
        if delta > reply_timeout:
            logging.info(f'Command "{update.message.text}" timed out '
                         f'({delta.seconds:.1f}s > {reply_timeout.seconds:.1f}s)')
            return

        if pass_args and inline:
            args = (inline_args, )

        if pass_query:
            args = (update.callback_query, ) + args

        if pass_update:
            args = (update, ) + args

        if pass_string:
            string = pull_string(bound_method.__self__.message_text)

            args = (string, ) + args

        return bound_method(*args, **kwargs)

    return wrapped


def command(arg=None, *, pass_args=None, pass_update=False, pass_string=False,
            register_help=True, allow_inline=False, **kwargs):
    """
    Generates a command decorator (see `command_decorator`).
    All **kwargs are for either
        - configuring of the decorator generation
        - configuring of the function wrapped by the decorator
        - configuring of the telegram.Dispatcher, which will
            finally call the wrapped function

    Can be used directly as `@command`, in which case the argument to this
    meta-wrapper (which will be the callable itself, instead of any actual
    arguments) will be forwarded to `command_decorator`

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
        """
        Decorate `method` by adding
            - a callable `handler` attribute to the method, which will take
                a `bound_method`, wrap it in yet another layer of meta-decoration,
                which will in turn create the appropriate handler for the dispatcher.
            - a callable `get_inner`, which takes a `bound_method` and creates
                the internal callable for said dispatchable.
            - some data members to reflect the type of command

        And finally
            - wrapping `method` in the `handle_herberrors` decorator

        """
        # FIXME/NOTE that said, i still do not get why get_inner doesn't just use `method`?
        # there is no reason afaik to duplicate the callable for each alias

        # This is necessary because the method itself is called as
        # `cls.method(self, *args)`, but the callback wants the bound method
        # that only takes `*args`. The bound method can only be constructed
        # with the actual instance, which is only known to `Herbert`.
        if not callable(method):
            raise ValueError(f'{method} not callable. Did you use @command()?')

        def get_inner(bound_method):
            inner_callback = pull_bot_and_update(
                bound_method,
                pass_update=pass_update,
                pass_query=False,
                pass_string=pass_string,
                pass_args=pass_args
            )
            return inner_callback

        def handler(name, bound_method):
            return CommandHandler(
                name, get_inner(bound_method), pass_args=pass_args, **kwargs)

        method.get_inner = get_inner
        method.command_handler = handler
        method.register_help = register_help
        method.commands = [method.__name__]
        method.inline = allow_inline
        return handle_herberrors(method)

    if callable(arg):
        return command_decorator(arg)

    return command_decorator


def aliases(*args):
    """
    Creates a decorator for adding propertied to a function
    decorated by `@command`.
    """
    def decorator(method):
        """
        Push the arguments passed to `aliases` in
        the commands-list created by the command-
        decorator
        """
        try:
            method.commands.extend(args)
            return method

        except AttributeError:
            raise ValueError('Only command-decorated methods an have aliases')

    return decorator


def callback(arg=None, *, pass_update=False, pass_query=True, **kwargs):
    def callback_decorator(method):
        def handler(bound_method):
            inner_callback = pull_bot_and_update(
                bound_method, pass_update, pass_query)
            return CallbackQueryHandler(inner_callback, **kwargs)

        method.callback_query_handler = handler
        return handle_herberrors(method)

    if callable(arg):
        return callback_decorator(arg)

    return callback_decorator
