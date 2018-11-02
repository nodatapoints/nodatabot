import telegram
from functools import wraps
from io import BytesIO
from re import split

BOT_ERR_PREFIX = "`[ERR][ :( ] `"

MSG_CHUNK = 4096
MAX_CHUNKY_LENGTH = 3 * MSG_CHUNK

CALLBACK_ARGUMENT_SEPARATOR = " "


def _t_reply_chunky(bot, update, msg, **kwargs):
    '''
    The telegram message length is limited to MSG_CHUNK.
    To send more than that amount of bytes, it needs
    to be split into several messages. On retrieving
    webpages, this might happen, so this function
    takes care of that.

    @brief split a message into MSG_CHUNK-sized bits
    @param bot @see get
    @param update @see get
    @param msg the full-length message
    '''
    while msg:
        _t_reply(bot, update, msg[:MSG_CHUNK], parse_mode=None, **kwargs)
        msg = msg[MSG_CHUNK:]


def _t_reply_filed_utf8(bot, update, msg, name="default.txt", **kwargs):
    '''
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.

    @brief send message data as a document
    @param bot @see get
    @param update @see get
    @param msg the raw string data, utf-8 encoded
    @param name the filename
    '''
    _t_reply_filed_binary(bot, update, bytes(msg, encoding="utf-8"), name=name, **kwargs)


def _t_reply_filed_binary(bot, update, data, name="default", **kwargs):
    '''
    To avoid spamming the user, a lot of data can be
    packed in a file and then sent at once.

    @brief send message data as a document
    @param bot @see get
    @param update @see get
    @param msg the raw data, as a byte stream
    @param name the filename
    '''
    f = BytesIO(data)
    f.seek(0)
    f.name = name

    bot.send_document(update.message.chat_id, document=f, **kwargs)


def _t_reply_large_utf8(bot, update, msg, name, **kwargs):
    '''
    Determine whether to send the message chunked
    or filed, and then forward the data

    @brief send data to the user
    @param bot @see get
    @param update @see get
    @param msg string data
    @param name if the file output gets chosen, this
                specifies the corresponding name
    '''
    if len(msg) > MAX_CHUNKY_LENGTH:
        _t_reply_filed_utf8(bot, update, msg, name, **kwargs)
    else:
        _t_reply_chunky(bot, update, msg, **kwargs)


def _t_reply(bot, update, msg, parse_mode=telegram.ParseMode.MARKDOWN, **kwargs):
    '''
    Forward a message to the client using the bot API.
    This will always target the chat which triggered
    the request to this herbert submodule.
    Set Markdown enabled by default.

    @brief send a message
    @param bot @see get
    @param update @see get
    @param msg a string with len(msg) <= MSG_CHUNK
    '''
    bot.send_message(update.message.chat_id, text=str(msg), parse_mode=parse_mode, **kwargs)


def _t_reply_err(bot, update, msg):
    '''
    wrap errors in a uniform way. Sends a message back to
    the client, containing the error prefix and the error
    message.

    @brief Error reply function
    @param bot @see get
    @param update @see get
    @param msg the error message. must be convertible to str
    '''
    for sub in split("\n", str(msg)):
        _t_reply(bot, update, BOT_ERR_PREFIX + sub)


# hell yeah
def _t_make_keyboard(button_dict):
    '''
    encode a dict as a telegram keyboard.
    nested dicts are buttons on a single line.
    @param
    '''
    return telegram.InlineKeyboardMarkup(
        [[telegram.InlineKeyboardButton(key, callback_data=val) for key, val in val.items()]
         if type(val) is dict else [telegram.InlineKeyboardButton(key, callback_data=val)]
         for key, val in button_dict.items()]
    )


def _t_get_photo(param):
    '''
    wrap the given param in a telegram bot object.
    can be a file or a url or a bytestream or something

    @brief wrap a photo for telegramming
    @param the data to wrap
    @returns a telegram.InputMediaPhoto object
    '''
    return telegram.InputMediaPhoto(param)


def _t_make_callback(name, *args):
    res = "T" + name
    for a in args:
        res += CALLBACK_ARGUMENT_SEPARATOR + str(a)

    return res


def _tx_callback(handler):
    @wraps(handler)
    def wrapper(bot, update):
        query = update.callback_query
        elements = split(CALLBACK_ARGUMENT_SEPARATOR, query.data)

        handler(bot, update, elements[0], elements[1:])

    return wrapper


__all__ = ['_t_reply', '_t_reply_filed_utf8', '_t_reply_filed_binary', '_t_reply_chunky',
           '_t_reply_large_utf8', '_t_make_keyboard', '_t_make_callback', '_t_get_photo',
           '_tx_callback']
