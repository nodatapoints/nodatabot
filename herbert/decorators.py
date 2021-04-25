"""
Define all the decorators!
"""
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable
import re

import telegram.error
from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update

from common.basic_decorators import argdecorator
from common.herbert_utils import is_cmd_decorated
from common.constants import ERROR_FAILED, ERROR_TEMPLATE, \
    BAD_ERROR_TEMPLATE, EMOJI_EXPLOSION, EMOJI_WARN, ONLY_BASIC_HELP
from common.chatformat import render_style_para
from common.prefixhandler import HerbotPrefixHandler
from common import reply_data

from herberror import Herberror, BadHerberror

__all__ = [
    'pull_string', 'handle_herberrors', 'pull_bot_and_update',
    'command', 'aliases', 'callback', 'doc'
]

reply_timeout = timedelta(seconds=120)


def pull_string(text):
    """
    Discard command name of command message
    e.g. transform `/do something` into `something`
    """
    splits = re.split(r'\s', text, 1)
    return splits[1] if len(splits) >= 2 else ""


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

        except Herberror as error:
            template = ERROR_TEMPLATE
            emoji = EMOJI_WARN
            if isinstance(error, BadHerberror):
                template = BAD_ERROR_TEMPLATE
                emoji = EMOJI_EXPLOSION

            res_text = template.format(emoji, " ".join(error.args))
            self.reply_text(res_text, disable_web_page_preview=True)
            msg, = error.args
            logging.getLogger('herbert.RUNTIME').debug('Herberror: "%s"', msg)

        except telegram.error.TimedOut:
            logging.getLogger('herbert.RUNTIME') \
                   .info('Timed out')

        except telegram.error.NetworkError:
            logging.getLogger('herbert.RUNTIME') \
                   .info('Connection Failed or message rejected by telegram API')

        except Exception:
            self.reply_text(ERROR_FAILED)
            raise

        return None

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
    def wrapped(update: Update, context: CallbackContext, inline=False, inline_query=None,
                inline_args=None, **kwargs):

        if inline_args is None:
            inline_args = []

        args = (context.args,) if pass_args else tuple()

        # bound_method.__self__.bot = context.bot
        # bound_method.__self__.update = update
        # bound_method.__self__.inline = inline
        # bound_method.__self__.inline_query = inline_query
        # update.message = None bei edits

        bound_method.__self__.context = (
            reply_data.InlineContext(context.bot, inline_query) if inline else
            reply_data.ChatContext(context.bot, update.message)
        )

        if update.message is not None:
            delta = datetime.now().astimezone() - update.message.date.replace()
            if delta > reply_timeout:
                logging.getLogger('herbert.RUNTIME') \
                       .info('Command "%s" timed out (%.1fs > %.1fs)',
                             update.message.text, delta.seconds,
                             reply_timeout.seconds)
                return None

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
    """
    Encode which information should be passed to
    a given command handler
    """
    STRING, ARGS, UPDATE, QUERY = 1, 2, 4, 8

    @staticmethod
    def value(pass_string, pass_args, pass_update, pass_query):
        """
        Generate an integer representation from four boolean values
        for the different argument types
        """
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

    def __init__(self, method, alias_list, register_help, help_summary, help_detailed,
                 pass_info=PassedInfoType.STRING, allow_inline=False, **ptb_args):
        self.aliases = alias_list
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
        """
        Create an instance of this class for a given method, by supplying the
        method name as the default command name and substituting default values
        otherwise
        """
        summary, fulltext = HerbertCmdHandlerInfo.extract_help(method, register_help)
        return HerbertCmdHandlerInfo(
            method,
            [method.__name__],
            register_help,
            summary,
            fulltext,
            **kwargs
        )

    @staticmethod
    def extract_help(method, register_help):
        """
        Parse the docstring looking for levels of documentation
        for any given command
        """
        if not register_help:
            return '', ''

        if not method.__doc__:
            logging.getLogger('herbert.SETUP') \
                   .info("/%s is missing ALL Documentation!", method.__name__)
            return '', ''

        # re.split will return either one or two results
        summary, *fulltext = re.split('\n\n', method.__doc__, maxsplit=1)

        if register_help == ONLY_BASIC_HELP:
            return summary, 'This should be self-explanatory. If you really ' \
                            'need help, sucks to be you; go look at the code.'

        if len(fulltext) == 0:
            logging.getLogger('herbert.SETUP') \
                   .info("/%s is missing detailed Documentation!", method.__name__)
            return summary, ''

        return (summary, *fulltext)

    def handlers(self, member_method):
        """
        Generate the handlers ptb needs to call the function this is attached to
        """
        def handlerfor(name):
            return HerbotPrefixHandler(name, self.invoke(member_method), **self.ptb_forward)

        return (handlerfor(name) for name in self.aliases)

    def invoke(self, member_method):
        return pull_bot_and_update(
            member_method,
            pass_update=self.pass_info & PassedInfoType.UPDATE != 0,
            pass_query=self.pass_info & PassedInfoType.QUERY != 0,
            pass_string=self.pass_info & PassedInfoType.STRING != 0,
            pass_args=self.pass_info & PassedInfoType.ARGS != 0
        )


@argdecorator
def command(*args, pass_args=None, pass_update=False, pass_string=False,
            register_help=True, allow_inline=False, **kwargs):
    """
    Attach this decorator to a method to generate a HerbertCmdHandlerInfo,
    which is in turn used in `core.py` to identify command handlers.
    The wrapped function will be called with the appropriate arguments.
    """

    method, *args = args

    if len(args) > 1:
        logging.getLogger('herbert.SETUP') \
               .warning('Ignoring arguments to @command (%s) on %s', args, method.__name__)

    pass_args = pass_args if pass_args is not None else not pass_string
    pass_info = PassedInfoType.value(pass_string, pass_args, pass_update, False)

    method.cmdinfo = HerbertCmdHandlerInfo.generatefor(
        method,
        pass_info=pass_info,
        allow_inline=allow_inline,
        register_help=register_help,
        **kwargs
    )

    return handle_herberrors(method)


@argdecorator
def aliases(method, *args):
    """
    Add an alias to the HerbertCmdHandlerInfo, which already has to
    be present on `method`. Will allow other Telegram commands to call
    the decorated function (the default command is the function name)
    """
    if is_cmd_decorated(method):
        method.cmdinfo.aliases.extend(args)
    else:
        raise ValueError('Only command-decorated methods can have aliases')
    return method


@argdecorator
def callback(method=None, *, pass_update=False, pass_query=True, **kwargs):
    """
    Construct a ptb CallbackQueryHandler, to mark the decorated function
    as an entrypoint for button clicks etc.
    """
    def handler(bound_method):
        inner_callback = pull_bot_and_update(
            bound_method, pass_update, pass_query)
        return CallbackQueryHandler(inner_callback, **kwargs)

    method.callback_query_handler = handler
    return handle_herberrors(method)


@argdecorator
def doc(method: Callable, docstring: str):
    """
    Change the docstring of a function to the argument of this decorator
    This can be used to use f-strings to use inline-parameters on the
    documentation
    """

    if is_cmd_decorated(method):
        logging.getLogger('herbert.SETUP') \
               .warning('calling @doc on already decorated method! '
                        'In the current version, @doc has to be applied before @command')

    method.__doc__ = render_style_para(docstring)
    return method
