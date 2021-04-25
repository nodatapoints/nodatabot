"""
Utilities for interfacing with the telegram api
"""
from functools import wraps
from io import BytesIO
from re import split
import hashlib

import telegram

from common.telegram_limits import MSG_CHUNK

BOT_ERR_PREFIX = "`[ERR][ :( ] `"

MAX_CHUNKY_LENGTH = 3 * MSG_CHUNK
CALLBACK_ARGUMENT_SEPARATOR = " "


def reply_chunky(bot, update, msg, parse_mode=None, **kwargs):
    """
    The telegram message length is limited to MSG_CHUNK.
    To send more than that amount of bytes, it needs
    to be split into several messages. On retrieving
    web pages, this might happen, so this function
    takes care of that.
    """
    while msg:
        reply(bot, update, msg[:MSG_CHUNK], parse_mode=parse_mode, **kwargs)
        msg = msg[MSG_CHUNK:]


def reply_filed_utf8(bot, update, msg, name="default.txt", **kwargs):
    """
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.
    """
    reply_filed_binary(bot, update, bytes(msg, encoding="utf-8"), name=name, **kwargs)


def reply_filed_binary(bot, update, data, name="default", **kwargs):
    """
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.
    """
    file = BytesIO(data)
    file.seek(0)
    file.name = name

    bot.send_document(update.message.chat_id, document=file, **kwargs)


def reply_large_utf8(bot, update, msg, max_chunky=MAX_CHUNKY_LENGTH, **kwargs):
    """
    Determine whether to send the message chunked
    or filed, and then forward the data
    """
    if len(msg) > max_chunky:
        reply_filed_utf8(bot, update, msg, **kwargs)
    else:
        reply_chunky(bot, update, msg, **kwargs)


def reply(bot, update, msg, parse_mode=telegram.ParseMode.MARKDOWN, **kwargs):
    """
    Forward a message to the client using the bot API.
    This will always target the chat which triggered
    the request to this herbert submodule.
    Set Markdown enabled by default.
    """
    send_message(bot, update.message.chat_id, text=str(msg), parse_mode=parse_mode, **kwargs)


def reply_err(bot, update, msg):
    """
    wrap errors in a uniform way. Sends a message back to
    the client, containing the error prefix and the error
    message.
    """
    for sub in split("\n", str(msg)):
        reply(bot, update, BOT_ERR_PREFIX + sub)


def _split_dict(dct, *keysets):
    for keys in keysets:
        yield {key: arg for key, arg in dct.items() if key in keys}
    yield {key: arg for key, arg in dct.items() if key not in set.union(*keysets)}


def send_message(bot, chat_id, text, **kwargs):
    """
    Call bot.send_message, where we pass the exakt kwargs that
    ptb wants directly, and everything else through api_kwargs
    """

    ptb_keys = (
        'parse_mode',
        'disable_web_page_preview',
        'reply_to_message_id',
        'reply_markup',
        'timeout',
        'allow_sending_without_reply',
        'entities'
    )

    chat_keys = (
        'edit_id'
    )

    ptb_args, fwd, options = _split_dict(kwargs, ptb_keys, chat_keys)

    ptb_args['chat_id'] = chat_id
    ptb_args['text'] = text
    ptb_args['api_kwargs'] = fwd

    if 'edit_id' in options:
        ptb_args.message_id = options['edit_id']

        bot.edit_message_text(**ptb_args)

    else:
        bot.send_message(**ptb_args)


def make_keyboard(button_dict):
    """
    encode a dict as a telegram keyboard.
    nested dicts are buttons on a single line.
    """
    return telegram.InlineKeyboardMarkup(
        [[telegram.InlineKeyboardButton(key, callback_data=val) for key, val in val.items()]
         if isinstance(val, dict) else [telegram.InlineKeyboardButton(key, callback_data=val)]
         for key, val in button_dict.items()]
    )


def reply_photo(bot, update, image_data, **kwargs):
    """
    Forward the given data as an image
    """
    bot.send_photo(update.message.chat_id, image_data, **kwargs)


def reply_image(bot, update, image_data, filename="image.png", high_res=False, **kwargs):
    """
    Send Image data. Use high_res=... to decide wheter to send it compressed
    or as a file.
    """
    if high_res:
        reply_filed_binary(bot, update, image_data, filename, **kwargs)
    else:
        reply_photo(bot, update, image_data, **kwargs)


def get_photo(param):
    """
    wrap the given param in a telegram bot object.
    can be a file or a url or a bytestream or something
    """
    return telegram.InputMediaPhoto(param)


CALLBACK_DATA_STORE = {}


def make_callback(name, *args):
    """
    Keep data between Telegram API calls by generating a key
    and placing the data in CALLBACK_DATA_STORE

    this is useful for answering inline queries, since only 64 byte
    can be cached on telegram side (which is enough for the generated key)
    """
    prefix = "T" + name + CALLBACK_ARGUMENT_SEPARATOR
    res = prefix + CALLBACK_ARGUMENT_SEPARATOR.join(args)

    key = prefix + CALLBACK_ARGUMENT_SEPARATOR + hashlib.md5(res.encode("utf-8")).hexdigest()

    CALLBACK_DATA_STORE[key] = res

    return key


def make_tx_callback(handler):
    """
    convert a regular command handler into a callback handler
    by restoring the argument data from CALLBACK_DATA_STORE
    """
    @wraps(handler)
    def wrapper(self, query):
        stored_data = CALLBACK_DATA_STORE[query.data]
        _name, *args = split(CALLBACK_ARGUMENT_SEPARATOR, stored_data)

        return handler(self, query, args)

    return wrapper


__all__ = ['reply', 'reply_filed_utf8', 'reply_filed_binary', 'reply_chunky',
           'reply_large_utf8', 'make_keyboard', 'make_callback', 'get_photo',
           'make_tx_callback']
