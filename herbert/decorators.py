"""
Define all the decorators!
"""
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable
import re

import telegram.error
from telegram.ext import CommandHandler, CallbackQueryHandler

from basebert import Herberror, BadHerberror
from common.constants import ERROR_FAILED, ERROR_TEMPLATE, BAD_ERROR_TEMPLATE, \
    EMOJI_EXPLOSION, EMOJI_WARN

__all__ = ['pull_string', 'handle_herberrors', 'pull_bot_and_update', 'command', 'aliases', 'callback', 'doc']

reply_timeout = timedelta(seconds=30)


def argdecorator(fn):
    """ 
    decorator decorating a decorator, to convert it to a decorator-generating function.
    """

    def argreceiver(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            # logging.getLogger('herbert.SETUP').warn(
            # f'{args[0].__name__} (?, name lookup might fail here) has missing parentheses on @{fn.__name__}')
            return fn(*args, **kwargs)
        return lambda method: fn(method, *args, **kwargs)

    return argreceiver


def pull_string(text):  # FIXME requires documentation
    _, _, string = text.partition(' ')
    return string


def is_cmd_decorated(fn):
    return hasattr(fn, 'cmdinfo')


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
            template = ERROR_TEMPLATE
            emoji = EMOJI_WARN
            if isinstance(e, BadHerberror):
                template = BAD_ERROR_TEMPLATE
                emoji = EMOJI_EXPLOSION

            res_text = template.format(emoji, " ".join(e.args))
            self.reply_text(res_text, disable_web_page_preview=True)
            msg, = e.args
            logging.getLogger('herbert.RUNTIME').debug(f'Herberror: "{msg}"')

        except telegram.error.TimedOut:
            logging.getLogger('herbert.RUNTIME').info('Timed out')
        except telegram.error.NetworkError:
            logging.getLogger('herbert.RUNTIME').info('Connection Failed')

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
                inline_args=None, **kwargs):

        if inline_args is None:
            inline_args = []

        bound_method.__self__.bot = bot
        bound_method.__self__.update = update
        bound_method.__self__.inline = inline
        bound_method.__self__.inline_query = inline_query
        # update.message = None bei edits

        if update.message is not None:
            delta = datetime.now() - update.message.date
            if delta > reply_timeout:
                logging.getLogger('herbert.RUNTIME') \
                    .info(f'Command "{update.message.text}" timed out '
                          f'({delta.seconds:.1f}s > {reply_timeout.seconds:.1f}s)')
                return

        if pass_args and inline:
            args = (inline_args,)

        if pass_query:
            args = (update.callback_query,) + args

        if pass_update:
            args = (update,) + args

        if pass_string:
            string = pull_string(bound_method.__self__.message_text)

            args = (string,) + args

        return bound_method(*args, **kwargs)

    return wrapped


class PassedInfoType:
    STRING, ARGS, UPDATE, QUERY = 1, 2, 4, 8

    @staticmethod
    def value(pass_string, pass_args, pass_update, pass_query):
        return (PassedInfoType.STRING if pass_string else 0) + \
               (PassedInfoType.ARGS if pass_args else 0) + \
               (PassedInfoType.UPDATE if pass_update else 0) + \
               (PassedInfoType.QUERY if pass_query else 0)


class HerbertCmdHandlerInfo:
    """
    Store all the data that was previously stored as
    several method members into a single object,
    to reduce my ide being confused and increase
    not having to check for each individual attribute
    """

    def __init__(self, method, aliases, register_help, help_summary, help_detailed,
                 pass_info=PassedInfoType.STRING, allow_inline=False, **ptb_args):
        self.aliases = aliases
        self.method = method  # to add handlers we still need an actual instance
        self.register_help = register_help
        self.help_summary, self.help_detailed = help_summary, help_detailed
        self.pass_info = pass_info
        self.allow_inline = allow_inline
        self.ptb_forward = ptb_args
        self.callback_query_handler = None

        self.cache_err_handled_method = None

    @staticmethod
    def generatefor(method, register_help=True, **kwargs):
        h1, h2 = HerbertCmdHandlerInfo.extractHelp(method, register_help)
        return HerbertCmdHandlerInfo(method, [method.__name__], register_help, h1, h2, **kwargs)

    @staticmethod
    def extractHelp(method, register_help):
        if not register_help:
            return '', ''
        if not method.__doc__:
            logging.getLogger('herbert.SETUP').info(f"/{method.__name__} is missing ALL Documentation!")
            return '', ''
        p1, *p2 = re.split('\n\n', method.__doc__, maxsplit=1)
        if len(p2) == 0:
            logging.getLogger('herbert.SETUP').info(f"/{method.__name__} is missing detailed Documentation!")
            return p1, ''
        return (p1, *p2)

    def handlers(self, member_method):
        def handlerfor(name):
            return CommandHandler(name, self._invoke(member_method),
                                  pass_args=self.pass_info & PassedInfoType.ARGS, **self.ptb_forward)

        return (handlerfor(name) for name in self.aliases)

    def _invoke(self, member_method):
        return pull_bot_and_update(
            member_method,
            pass_update=self.pass_info & PassedInfoType.UPDATE,
            pass_query=self.pass_info & PassedInfoType.QUERY,
            pass_string=self.pass_info & PassedInfoType.STRING,
            pass_args=self.pass_info & PassedInfoType.ARGS
        )


@argdecorator
def command(method, *args, pass_args=None, pass_update=False, pass_string=False,
            register_help=True, allow_inline=False, **kwargs):

    if args:
        logging.getLogger('herbert.SETUP').warning(f'Ignoring arguments to @command ({args}) on {method.__name__}')

    pass_args = pass_args if pass_args is not None else not pass_string
    pass_info = PassedInfoType.value(pass_string, pass_args, pass_update, False)

    method.cmdinfo = HerbertCmdHandlerInfo.generatefor(method,
                                                       pass_info=pass_info, allow_inline=allow_inline,
                                                       register_help=register_help, **kwargs)

    return handle_herberrors(method)


@argdecorator
def aliases(method, *args):
    if is_cmd_decorated(method):
        method.cmdinfo.aliases.extend(args)
    else:
        raise ValueError('Only command-decorated methods can have aliases')
    return method


@argdecorator
def callback(method=None, *, pass_update=False, pass_query=True, **kwargs):
    def handler(bound_method):
        inner_callback = pull_bot_and_update(
            bound_method, pass_update, pass_query)
        return CallbackQueryHandler(inner_callback, **kwargs)

    method.callback_query_handler = handler
    return handle_herberrors(method)


@argdecorator
def doc(method, docstring):
    from common.chatformat import render_style_para as r

    if is_cmd_decorated(method):
        logging.getLogger('herbert.SETUP').warning('calling @doc on already decorated method! '
                                                   'In the current version, @doc has to be applied before @command')

    method.__doc__ = r(docstring)
    return method
