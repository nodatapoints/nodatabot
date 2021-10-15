"""
Define all the decorators!
"""
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, TypeVar, List
from dataclasses import dataclass
import re

import telegram.error
from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update

from basebert import BaseBert
from common.basic_decorators import argdecorator
from common.herbert_utils import is_cmd_decorated
from common.constants import ERROR_FAILED, ERROR_TEMPLATE, \
    BAD_ERROR_TEMPLATE, EMOJI_EXPLOSION, EMOJI_WARN, ONLY_BASIC_HELP
from common.chatformat import render_style_para, STYLE_BACKEND
from common.prefixhandler import HerbotPrefixHandler
from common import reply_data

from herberror import Herberror, BadHerberror

__all__ = [
    'pull_string', 'handle_herberrors', 'pull_bot_and_update',
    'command', 'aliases', 'callback', 'doc'
]

reply_timeout = timedelta(seconds=120)
Ret = TypeVar('Ret')


def pull_string(text: str) -> str:
    """
    Discard command name of command message
    e.g. transform `/do something` into `something`
    """
    splits = re.split(r'\s', text, 1)
    return splits[1] if len(splits) >= 2 else ""


def handle_herberrors(method: Callable[[BaseBert, ...], Ret]) -> Callable[[BaseBert, ...], Ret]:
    """
    Returns a wrapper around `method`, which in turn
    Catches `Herberror` and sends the argument of the exception as a message
    to the user. When an exception of any other type is caught, it will send
    a default error message to the user and raise it again.
    """

    @wraps(method)
    def wrapped(self: BaseBert, *args, **kwargs):
        """
        Functional wrapper to handle errors a command_handler
        might throw as well as errors that are entirely unexpected
        """
        log = logging.getLogger('herbert.RUNTIME')

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
            log.debug('Herberror: "%s"', msg, exc_info=error)

        except telegram.error.TimedOut:
            log.info('Timed out')

        except telegram.error.NetworkError:
            log.info('Connection Failed or message rejected by telegram API')

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


@dataclass
class PassedInfoType:
    """
    Property of a command handler, describing which
    arguments should be passed to the handling function

    pass_string: the full text of the invocation message
    pass_args: an array containing the words of the invocation,
        excluding the command itself
    pass_update: the telegram update object
    pass_query: the telegram query object
    """
    pass_string: bool = False
    pass_args: bool = False
    pass_update: bool = False
    pass_query: bool = False


@dataclass
class CmdHandlerProperties:
    """
    Data used by the HerbertCmdHandlerInfo
    """
    aliases: List[str]
    register_help: bool
    help_summary: str
    help_detailed: str
    pass_info: PassedInfoType = PassedInfoType(pass_string=True)
    allow_inline: bool = False


class HerbertCmdHandlerInfo:
    """
    Store all the data that was previously stored as
    several method members into a single object,
    to reduce my ide being confused and increase
    not having to check for each individual attribute
    """

    def __init__(self, method, properties: CmdHandlerProperties, **ptb_args):
        self.properties = properties
        self.method = method  # to add handlers we still need an actual instance
        self.ptb_forward = ptb_args
        self.callback_query_handler = None
        self.cache_err_handled_method = None

    @staticmethod
    def generatefor(method, pass_info, allow_inline=False, register_help=True, **kwargs):
        """
        Create an instance of this class for a given method, by supplying the
        method name as the default command name and substituting default values
        otherwise
        """

        summary, fulltext = HerbertCmdHandlerInfo.extract_help(method, register_help)
        return HerbertCmdHandlerInfo(
            method,
            CmdHandlerProperties(
                pass_info=pass_info,
                allow_inline=allow_inline,
                aliases=[method.__name__],
                register_help=register_help,
                help_summary=summary,
                help_detailed=fulltext
            ),
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

        return (handlerfor(name) for name in self.properties.aliases)

    def invoke(self, member_method):
        """
        Function that gets invoked by the HerbotPrefixHandler
        Propagates call to the actual command handler
        """
        pass_info = self.properties.pass_info
        return pull_bot_and_update(
            member_method,
            pass_update=pass_info.pass_update,
            pass_query=pass_info.pass_query,
            pass_string=pass_info.pass_string,
            pass_args=pass_info.pass_args
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
    pass_info = PassedInfoType(pass_string, pass_args, pass_update, False)

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
        method.cmdinfo.properties.aliases.extend(args)
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

    method.__doc__ = render_style_para(docstring, target_style=STYLE_BACKEND)
    return method
