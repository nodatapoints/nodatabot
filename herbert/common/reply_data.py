"""
Store things that can be replied,
as well as ways *how* the things can
be replied.
"""
from dataclasses import dataclass, field
from typing import List, Union, Optional
from io import BytesIO

from telegram import Bot, CallbackQuery, InlineQuery, Message
import telegram


@dataclass
class ReplyData:
    """
    Super class

    All instances of this class represent some
    kind of data to be returned back to the
    telegram API

    This is agnostic of the invocation context
    (CallbackQuery/Edit/Normal send), but will
    do no further reshaping, so the messages
    should be parsed and potentially transformed
    into files or whatever before being handed
    over to a send method
    """
    reply_markup: Optional[telegram.ReplyMarkup] = field(default=None, init=False)


@dataclass
class Text(ReplyData):
    """ replies consisting of simple, possibly markupped text """
    msg: str
    entities: list = field(default_factory=lambda: [])
    name: Optional[str] = None  # in case this gets converted to a file
    disable_web_page_preview: bool = False


@dataclass
class Captionable(ReplyData):
    """ common superclass for all messages with captions """
    caption: Union[Text, str]


@dataclass
class Sticker(ReplyData):
    """ sticker message """
    sticker: str


@dataclass
class File(Captionable):
    """ upload a file """
    data: BytesIO
    name: str


@dataclass
class Gif(Captionable):
    """ send a url to an (animated) gif """
    url: str


@dataclass
class Photo(Captionable):
    """ upload a photo """
    data: BytesIO


@dataclass
class PhotoUrl(Captionable):
    """ send a url to some image """
    url: str


@dataclass
class Poll(ReplyData):
    """ create a poll """
    question: str
    options: List[str]
    is_anonymous: bool
    allow_multiple_answers: bool


# Context Types
@dataclass
class Context:
    """
    Super class

    All instances of this class represent some
    context via which data can be returned to
    the telegram API (e.g. chat_id, CallbackQuery
    object, etc)
    """
    bot: Bot


@dataclass
class ChatContext(Context):
    """ send into a normal chat """
    message: Message

    @property
    def chat_id(self):
        """
        access the id of the chat from which the command was invoked
        """
        return self.message.chat_id


@dataclass
class ChatEditContext(ChatContext):
    """ edit a message already sent to a chat """
    message_id: int


@dataclass
class InlineContext(Context):
    """ answer an @inline query """
    query: InlineQuery


@dataclass
class MessageCallbackContext(Context):
    """ answer an @inline query """
    query: CallbackQuery
