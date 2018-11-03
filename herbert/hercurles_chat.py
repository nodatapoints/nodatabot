import telegram
from functools import wraps
from io import BytesIO
from re import split
import hashlib

BOT_ERR_PREFIX = "`[ERR][ :( ] `"

MSG_CHUNK = 4096
MAX_CHUNKY_LENGTH = 3 * MSG_CHUNK

CALLBACK_ARGUMENT_SEPARATOR = " "


def _t_reply_chunky(bot, update, msg, parse_mode=None, **kwargs):
    """
    The telegram message length is limited to MSG_CHUNK.
    To send more than that amount of bytes, it needs
    to be split into several messages. On retrieving
    webpages, this might happen, so this function
    takes care of that.
    """
    while msg:
        _t_reply(bot, update, msg[:MSG_CHUNK], parse_mode=parse_mode, **kwargs)
        msg = msg[MSG_CHUNK:]


def _t_reply_filed_utf8(bot, update, msg, name="default.txt", **kwargs):
    """
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.
    """
    _t_reply_filed_binary(bot, update, bytes(msg, encoding="utf-8"), name=name, **kwargs)


def _t_reply_filed_binary(bot, update, data, name="default", **kwargs):
    """
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.
    """
    f = BytesIO(data)
    f.seek(0)
    f.name = name

    bot.send_document(update.message.chat_id, document=f, **kwargs)


def _t_reply_large_utf8(bot, update, msg, **kwargs):
    """
    Determine whether to send the message chunked
    or filed, and then forward the data
    """
    if len(msg) > MAX_CHUNKY_LENGTH:
        _t_reply_filed_utf8(bot, update, msg, **kwargs)
    else:
        _t_reply_chunky(bot, update, msg, **kwargs)


def _t_reply(bot, update, msg, parse_mode=telegram.ParseMode.MARKDOWN, **kwargs):
    """
    Forward a message to the client using the bot API.
    This will always target the chat which triggered
    the request to this herbert submodule.
    Set Markdown enabled by default.
    """
    bot.send_message(update.message.chat_id, text=str(msg), parse_mode=parse_mode, **kwargs)


def _t_reply_err(bot, update, msg):
    """
    wrap errors in a uniform way. Sends a message back to
    the client, containing the error prefix and the error
    message.
    """
    for sub in split("\n", str(msg)):
        _t_reply(bot, update, BOT_ERR_PREFIX + sub)


def _t_make_keyboard(button_dict):
    """
    encode a dict as a telegram keyboard.
    nested dicts are buttons on a single line.
    """
    return telegram.InlineKeyboardMarkup(
        [[telegram.InlineKeyboardButton(key, callback_data=val) for key, val in val.items()]
         if type(val) is dict else [telegram.InlineKeyboardButton(key, callback_data=val)]
         for key, val in button_dict.items()]
    )


def _t_get_photo(param):
    """
    wrap the given param in a telegram bot object.
    can be a file or a url or a bytestream or something
    """
    return telegram.InputMediaPhoto(param)


callback_data_store = {}


def _t_make_callback(name, *args):
    prefix = "T" + name + CALLBACK_ARGUMENT_SEPARATOR
    res = prefix + CALLBACK_ARGUMENT_SEPARATOR.join(args)

    key = prefix + CALLBACK_ARGUMENT_SEPARATOR + hashlib.md5(res.encode("utf-8")).hexdigest()

    callback_data_store[key] = res

    return key


def _tx_callback(handler):
    @wraps(handler)
    def wrapper(self, bot, update, *args, **kwargs):
        query = update.callback_query

        stored_data = callback_data_store[query.data]

        name, *args = split(CALLBACK_ARGUMENT_SEPARATOR, stored_data)

        handler(self, bot, update, name, args)

    return wrapper


__all__ = ['_t_reply', '_t_reply_filed_utf8', '_t_reply_filed_binary', '_t_reply_chunky',
           '_t_reply_large_utf8', '_t_make_keyboard', '_t_make_callback', '_t_get_photo',
           '_tx_callback']
