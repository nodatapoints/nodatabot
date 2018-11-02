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
from herbert_utils import *
from hercurles_network import *
from hercurles_utils import *
from hercurles_chat import *


# EXPOSE MEMBERS
__all__ = ["get_text", "get", "callback", "searchfor"]


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

    _t_reply_large_utf8(bot, update, _t_load_str(url), _t_gen_filename(url))


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


@command_handler('gettext', pass_args=True)
@bot_proxy
def get_text(bot, update, args):
    """
    These functions expose the functionality of the submodule
    to the bot and are exported from this file
    """
    _t_get_text(bot, update, args)


@command_handler('curl', pass_args=True)
@command_handler('getme', pass_args=True)
@bot_proxy
def get(bot, update, args):
    _t_get(bot, update, args)


@command_handler('searchfor', pass_args=True)
@bot_proxy
def searchfor(bot, update, args):
    _t_search_for(bot, update, args)


@callback_handler(pattern='T.*')
@bot_proxy
@_tx_callback
def callback(bot, update, name, args):
    """
    When clicking on a button, perform the appropriate event.
    This currently handles the following queries:
      - Show Image:
          ID: T0
          Params: <url>
          Action: Replace the given message with the image found at <url>
    """
    query = update.callback_query

    if name == "T0":
        bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=_t_get_photo(args[0]),
        )
    else:
        raise RuntimeError("Invalid Query Callback")
