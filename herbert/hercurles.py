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
from basebert import *
from decorators import *

from hercurles_network import *
from hercurles_utils import *
from hercurles_chat import *


# EXPOSE MEMBERS
__all__ = ["get_text", "get", "callback", "searchfor", "searchforfirst"]


ARG_COUNT_ERR = "This takes exactly 1 argument. Please try again."


def _t_get_text(bot, update, args):
    """
    This function forwards the request from the client
    to the handling functions, and then replies with
    the result or reports an error, if necessary.
    On success, forward the contents of an url specified
    in args to the end user.
    """
    assert len(args) == 1, ARG_COUNT_ERR

    url = args[0]

    _t_reply_large_utf8(bot, update, _t_load_str(url), name=_t_gen_filename(url))


def _t_get(bot, update, args):
    assert len(args) == 1, ARG_COUNT_ERR

    url = args[0]

    data_type, data = _t_load_content(url)

    _t_reply_filed_binary(bot, update, data, _t_gen_filename(url, data_type),
                          reply_markup=_t_make_keyboard(
                              {"Show as Photo": _t_make_callback("0", url)}
                          ) if _t_is_image(data_type) else None
                          )


def _t_search_for(bot, update, args):
    assert len(args) == 1, ARG_COUNT_ERR

    query_string = args[0]

    results = "\n".join(search_for(query_string))

    _t_reply_large_utf8(bot, update, results)


def _t_search_for_first(bot, update, args):

    query_string = " ".join(args)

    result = search_for(query_string)[0]

    _t_reply_large_utf8(bot, update, result)


class Hercurles(BaseBert):

    @aliases('gettext', 'get_text', 'gt')
    @command
    def get_text(self, args):
        """
        These functions expose the functionality of the submodule
        to the bot and are exported from this file
        """
        _t_get_text(self.bot, self.update, args)

    @aliases('getme', 'curl')
    @command
    def get(self, args):
        _t_get(self.bot, self.update, args)

    @command
    def searchfor(self, args):
        _t_search_for(self.bot, self.update, args)

    @aliases('lookup')
    @command
    def searchforfirst(self, args):
        _t_search_for_first(self.bot, self.update, args)

    @callback(pattern='T.*')
    @_tx_callback
    def callback(self, name, args):
        """
        When clicking on a button, perform the appropriate event.
        This currently handles the following queries:
          - Show Image:
              ID: T0
              Params: <url>
              Action: Replace the given message with the image found at <url>
        """
        query = self.update.callback_query

        if name == "T0":
            self.bot.edit_message_media(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                media=_t_get_photo(args[0]),
            )
        else:
            raise RuntimeError("Invalid Query Callback")
