##
# herbert submodule
#
# Allows to retrieve the contents of any webpage.
# To avoid spam, there is a cutoff after 100 chars
# with the option to show more.
#
# this is not how comments work in python. i know.
# and i do not care at all.
#

# IMPORTS
import telegram

from basebert import *
from decorators import *

from common.network import *
from common.hercurles_utils import *
from common.chat import *


# EXPOSE MEMBERS
__all__ = ['Hercurles']


ARG_COUNT_ERR = "This takes exactly 1 argument. Please try again."


def _t_get_text(bot: telegram.Bot, update: telegram.Update, url: str):
    """
    This function forwards the request from the client
    to the handling functions, and then replies with
    the result or reports an error, if necessary.
    On success, forward the contents of an url specified
    in args to the end user.
    """
    if " " in url:
        raise Herberror("URLS cannot contain spaces")

    reply_large_utf8(bot, update, load_str(url), name=gen_filename_from_url(url))


def _t_get(bot: telegram.Bot, update: telegram.Update, url: str):
    if " " in url:
        raise Herberror("URLS cannot contain spaces")

    data_type, data = load_content(url)

    reply_markup = make_keyboard({"Show as Photo": make_callback("0", url)}) if is_image_content_type(data_type) else None
    reply_filed_binary(bot, update, data, gen_filename_from_url(url, data_type), reply_markup=reply_markup)


def _t_search_for(bot, update, query):

    results = "\n".join(search_for(query))

    reply_large_utf8(bot, update, results)


def _t_search_for_first(bot, update, query):

    try:
        result = search_for(query)[0]
    except IndexError:
        result = "No Link found."

    reply_large_utf8(bot, update, result)


class Hercurles(BaseBert):

    @aliases('gt')
    @command(pass_string=True)
    @doc(""" Retrieve the contents of the given url as text or a text file """)
    def gettext(self, string):
        _t_get_text(self.bot, self.update, string.strip())

    @aliases('g', 'getme', 'curl')
    @command(pass_string=True)
    @doc(""" Retrieve the contents of the given url """)
    def get(self, string):
        _t_get(self.bot, self.update, string.strip())

    @command(pass_string=True)
    @doc(""" List the first few links the given string hits when searched for on DuckDuckGo """)
    def searchfor(self, string):
        _t_search_for(self.bot, self.update, string)

    @aliases('lookup')
    @command(pass_string=True)
    @doc(""" Return the first link the given string hits when searched for on DuckDuckGo """)
    def searchforfirst(self, string):
        _t_search_for_first(self.bot, self.update, string)

    @callback(pattern='T.*')
    @make_tx_callback
    def callback_fix(self, query, args):
        # I have no idea what I am doing. :)
        self.bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=get_photo(args[0]),
        )
