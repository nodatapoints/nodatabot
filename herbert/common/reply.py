"""
Provide methods for sending Messages to Telegram
"""

from copy import copy
import hashlib

from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from telegram.error import BadRequest

from common.telegram_limits import MSG_CHUNK
from common.basic_utils import arr_to_bytes, utf16len
from common.type_dispatch import TypeDispatch
from common.reply_data import (
    ReplyData,
    Context,

    Text,
    Captionable,
    Sticker,
    File,
    Gif,
    Photo,
    PhotoUrl,
    Poll,

    ChatContext,
    ChatEditContext,
    InlineContext,
)

# decorators are hard for the linter to understand
# pylint: disable=no-self-use,not-callable

__all__ = ['send_message']


def _gen_id(array):
    return hashlib.md5(arr_to_bytes(array))


def _inl_send(result, inline_query):
    try:
        inline_query.answer(result)
    except BadRequest:
        # answer time window passed
        pass


def _caption_args(c: Captionable):
    if c is None or c.caption is None:
        return dict()

    if isinstance(c.caption, str):
        return {
            'caption': c.caption,
            'caption_entities': []
        }

    return {
        'caption': c.caption.msg,
        'caption_entities': c.caption.entities
    }


def _inl_send_string_list(strings, query):
    result = [
        InlineQueryResultArticle(
            id=f"inline{i}-{_gen_id(strings)}",
            title=title,
            input_message_content=InputTextMessageContent(string)
        )
        for i, (string, title) in enumerate(strings)
    ]
    _inl_send(result, query)


def _inl_send_photo_url_list(photo_list, query):
    result = [
        InlineQueryResultPhoto(
            id=f"photo{i}-{_gen_id(photo_list)}",
            photo_url=url,
            title=caption,
            caption=caption,
            thumb_url=url
        ) for i, (url, caption) in enumerate(photo_list)
    ]
    _inl_send(result, query)


@TypeDispatch(ReplyData, Context)
class SendReply:
    """
    Take a message descriptor and an invocation context object
    and try to deliver the message to the right endpoint
    """

    # Text
    def edit_text(self, text: Text, ctx: ChatEditContext):
        ctx.bot.edit_message_text(text.msg, ctx.chat_id, ctx.message_id, reply_markup=text.reply_markup)

    def send_text(self, text: Text, ctx: ChatContext):
        ctx.bot.send_message(ctx.chat_id, text.msg, entities=text.entities, reply_markup=text.reply_markup)

    def query_answer_text(self, text: Text, ctx: InlineContext):
        _inl_send_string_list([(text.msg, text.msg)], ctx.query)

    # Sticker
    def send_sticker(self, sticker: Sticker, ctx: ChatContext):
        ctx.bot.send_sticker(ctx.chat_id, sticker.sticker, reply_markup=sticker.reply_markup)

    # File
    def send_file(self, file: File, ctx: ChatContext):
        ctx.bot.send_document(ctx.chat_id, document=file.data, filename=file.name, **_caption_args(file), reply_markup=file.reply_markup)

    # Gif
    def send_gif(self, gif: Gif, ctx: ChatContext):
        ctx.bot.send_animation(ctx.chat_id, animation=gif.url, reply_markup=gif.reply_markup)

    # Photo
    def send_photo(self, photo: Photo, ctx: ChatContext):
        ctx.bot.send_photo(ctx.chat_id, photo.data, **_caption_args(photo), reply_markup=photo.reply_markup)

    # PhotoUrl
    def send_photo_url(self, photo: PhotoUrl, ctx: ChatContext):
        ctx.bot.send_photo(ctx.chat_id, photo.url, **_caption_args(photo), reply_markup=photo.reply_markup)

    def inline_photo_url(self, photo: PhotoUrl, ctx: InlineContext):
        _inl_send_photo_url_list([(photo.url, photo.caption)], ctx.query)

    def send_poll(self, poll: Poll, ctx: ChatContext):
        ctx.bot.send_poll(
            ctx.chat_id,
            question=poll.question,
            options=poll.options,
            is_anonymous=poll.is_anonymous,
            allow_multiple_answers=poll.allow_multiple_answers,
            reply_markup=poll.reply_markup
        )


@TypeDispatch(ReplyData)
class TransformReply:
    """
    Reshape a message object, if sending would be impossible
    or impractical (very long texts etc.).
    """

    @staticmethod
    def _dispatch_fail(_classes, instances):
        return list(instances)

    def process_text(self, text: Text):
        """
        send a message in chunks if it is too long
        for a single telegram message
        """
        res = list()
        pos = 0
        size = utf16len(text.msg)

        while pos < size:
            end = min(size, pos + MSG_CHUNK)
            entities = list()
            for entity in text.entities:
                if (entity.offset in range(pos, end)
                        or entity.offset + entity.length in range(pos, end)
                        or (entity.offset < pos and entity.offset + entity.length > end)):
                    chunk_entity = copy(entity)
                    chunk_entity.offset = max(0, chunk_entity.offset - pos)
                    chunk_entity.length = min(chunk_entity.length, end - chunk_entity.offset)
                    entities.append(chunk_entity)

            res.append(Text(text.msg[pos:end], entities))
            pos = end

        return res

    def process_image(self, img: Photo):
        return [img]  # maybe actually do something


def processed_message_parts(data: ReplyData):
    yield from TransformReply()(data)


def send_message(data: ReplyData, ctx: Context):
    """
    Best-effort method for returning some piece of data
    to a command invocation. Will first apply some
    transformations, if needed, and then dispatch
    to the actual sending methods using the context
    type.
    """
    for part in processed_message_parts(data):
        SendReply()(part, ctx)
