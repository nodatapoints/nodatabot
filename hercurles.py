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
import urllib3
from urllib3.exceptions import HTTPError
import re
import certifi

from herbert_utils import *
from tim import *

# EXPOSE MEMBERS
__all__ = ["get_text", "get", "callback"]

# CONSTANTS
ARG_COUNT_ERR = "This takes exactly 1 argument. Please try again."
RESPONSE_STAT_ERR = "Invalid Response status"
NO_RESPONSE_ERR = "Could not connect to specified URL."
NOT_TEXT_ERR = "The requested web page couldn't be converted to text."

HTTP_STAT_OK = 200
REQUEST_TYPE_GET = "GET"

# fake it 'til you make it
USER_AGENT = {
    'user-agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'}

# GLOBAL
urllib3.disable_warnings()
http = urllib3.PoolManager(
    10, USER_AGENT, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


def _t_load(url):
    '''
    Interacts with urllib3 to send a GET request to a given URL.

    @brief retrieve the contents of a given website
    @param url the url to look up
    @returns a response obj containing the data, if the lookup
             was successful
    @throws a Herberror containing a description, if the
            lookup failed
    '''
    try:
        return http.request(REQUEST_TYPE_GET, url, retries=2)

    except HTTPError:
        raise Herberror(NO_RESPONSE_ERR)


#
# loads a webpage and tries to convert it to text
#
# @brief make a string from load()
# @param url the url to look up
# @returns a string containing the data, if the lookup
#          was successful
# @throws a Herberror containing a description, if the
#         lookup failed
#
def _t_load_str(url):
    res = _t_load(url)

    assert res.status == HTTP_STAT_OK, \
        f"{RESPONSE_STAT_ERR}: {res.status}\nResponse Header: `{res.headers}`"

    # this is actually necessary. loading even
    # google breaks with utf-8 text encoding
    charset = _t_extract_charset(res.headers)

    try:
        return res.data.decode(charset or 'utf-8')

    except UnicodeDecodeError:
        raise Herberror(NOT_TEXT_ERR)


def _t_load_content(url):
    '''
    loads a webpage from url, figures out the content type
    and returns it together with the pure binary data

    @brief get data and data type of a web page
    @param url the url to look up
    @returns a tuple of a content_type string and a binary data string
    '''
    res = _t_load(url)

    assert res.status == HTTP_STAT_OK, \
        f"{RESPONSE_STAT_ERR}: {res.status}"

    content_type = res.headers.get("Content-Type")
    content_type = re.split(";", content_type)[0]

    return content_type, res.data


def _t_is_image(content_type):
    '''
    @brief Checks whether content_type is the content type of an image
    @param content_type a utf8 encoded string
    @returns a boolean value depending on whether or not content_type
             is an image
    '''
    return content_type.startswith("image")


_ending = {
    "text/plain": "txt",
}


def _t_gen_filename(url, content_type="text/plain"):
    '''
    When replying with a file (@see _t_reply_filed),
    the file needs to get a name. in this context,
    the filename should reflect the original request
    url. This function encodes the url to allow it
    to be used as a filename

    @brief Converts a url to a filename
    @param url some url string
    @returns an arbitrary string meant to reflect the
             url and represent a file.
    '''
    return re.sub("[:/ \t\n]", "_", url) + "." + _ending.get(content_type, re.split("/", content_type)[1])


def _t_extract_charset(response_header):
    '''
    figure out the response character encoding from an http-
    header, if any.

    @brief get the character encoding from a header
    @param response_header a urllib3 response header
    @returns a string containing the name of the encoding
             or None if no encoding could be found.
    '''
    base = response_header.get("Content-Type")
    try:
        value = re.split("charset=", base)[1]
        value = re.split("(; ,)", value)[0]
        return value or None

    except IndexError:
        return None


def _t_get_text(bot, update, args):
    '''
    This function forwards the request from the client
    to the handling functions, and then replies with
    the result or reports an error, if necessary.
    On success, forward the contents of an url specified
    in args to the end user.

    @brief Get a webpage. Implementation.
    @param bot @see get
    @param update @see get
    @param args @see get
    '''
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


@command_handler('gettext', pass_args=True)
@bot_proxy
def get_text(bot, update, args):
    '''
    These functions expose the functionality of the submodule
    to the bot and are exported from this file

    @brief message handlers for this submodule
    @param bot a bot-object as specified by the python-telegram
           bot-api
    @param update the response object as specified by the python-
           telegram bot-api
    @param args the arguments to the bot command
    '''
    _t_get_text(bot, update, args)


@command_handler('curl', pass_args=True)
@command_handler('getme', pass_args=True)
@bot_proxy
def get(bot, update, args):
    _t_get(bot, update, args)


@callback_handler(pattern='T.*')
@bot_proxy
@_tx_callback
def callback(bot, update, name, args):
    '''
    When clicking on a button, perform the appropriate event.
    This currently handles the following queries:
      - Show Image:
          ID: T0
          Params: <url>
          Action: Replace the given message with the image found at <url>

    @brief telegram interactive callback funtion
    @param bot @see get
    @param update a python-telegram bot Update object with a nonempty
           callback_query
    @throws RuntimeError when called with an illegal update
    '''
    query = update.callback_query

    if name == "T0":
        bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=_t_get_photo(args[0]),
        )
    else:
        raise RuntimeError("Invalid Query Callback")
