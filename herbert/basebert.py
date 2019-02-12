from io import BytesIO
import hashlib

from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto, InlineQueryResultGif
import telegram.error

from common.basic_utils import arr_to_bytes
from common import chat, chatformat

__all__ = ['Herberror', 'BadHerberror', 'BaseBert', 'ImageBaseBert', 'InlineBaseBert']


class Herberror(Exception):
    """Basic Herbert error"""


class BadHerberror(Herberror):
    """Something someone needs to actually go and fix"""


class BaseBert:
    def __init__(self):
        self.bot = None
        self.update = None
        self.inline = False
        self.inline_query = None
        self.inline_args = []

    @property
    def message(self):
        if self.update.message:
            return self.update.message

        elif self.update.callback_query and self.update.callback_query.message:
            return self.update.callback_query.message

        else:
            return None

    @property
    def message_text(self):
        if self.message:
            return self.message.text

        elif self.inline_query:
            return self.inline_query.query

        else:
            return ""

    @property
    def query(self):
        return self.update.callback_query

    @property
    def chat_id(self):
        return self.message.chat_id

    def send_message(self, msg, parse_mode=chatformat.get_parse_mode(), **kwargs):
        if parse_mode == chatformat.STYLE_CUSTOM:
            msg = chatformat.render_custom(msg)

        return self.bot.send_message(
            self.chat_id,
            text=msg,
            parse_mode=chatformat.get_output_mode(use_style=parse_mode),
            **kwargs
        )

    def send_photo_from_file(self, path, **kwargs):
        return self.bot.send_photo(self.chat_id, open(path, 'rb'), **kwargs)

    def send_file(self, fname, data, **kwargs):
        chat.reply_filed_binary(self.bot, self.update, data, name=fname, **kwargs)

    def send_photo(self, data, **kwargs):
        self.bot.send_photo(self.chat_id, data, **kwargs)

    def send_gif(self, data, **kwargs):
        self.bot.send_animation(self.chat_id, data, **kwargs)

    # reply_ methods are a unified way to respond
    # both @inline and /directly.
    def reply_text(self, string, title='', **kwargs):
        title = title or string
        if self.inline:
            InlineBaseBert._inl_send_str_list([(string, title)], self.inline_query)
        else:
            self.send_message(string, **kwargs)

    def reply_photo_url(self, url, title="", caption=""):
        if self.inline:
            InlineBaseBert._inl_send_photo_url_list([(url, title, caption)], self.inline_query)
        else:
            self.send_photo(url, title=title, caption=caption)

    def reply_gif_url(self, url, title="", caption=""):
        if self.inline:
            InlineBaseBert._inl_send_gif_url_list([(url, title, caption)], self.inline_query)
        else:
            self.send_gif(url, title=title, caption=caption)

    @staticmethod
    def wrap_in_file(data, fname):
        f = BytesIO(data)
        f.name = fname
        return f


class InlineBaseBert(BaseBert):
    def inline_answer_string(self, string):
        self.inline_answer_strings([string])

    def inline_answer_strings(self, str_list):
        InlineBaseBert._inl_send_str_list(str_list, self.inline_query)

    @staticmethod
    def _inl_send_str_list(str_list, inline_query):
        result = [
            InlineQueryResultArticle(
                id=f"inline{i}-{InlineBaseBert.gen_id(str_list)}",
                title=title,
                input_message_content=InputTextMessageContent(string)
            )
            for i, (string, title) in enumerate(str_list)
        ]

        InlineBaseBert._inl_send(result, inline_query)

    def inline_answer_photo_url(self, url, title="", caption=""):
        self.inline_answer_photo_urls([(url, title, caption)])

    def inline_answer_photo_urls(self, url_list):
        InlineBaseBert._inl_send_photo_url_list(url_list, self.inline_query)

    @staticmethod
    def _inl_send_photo_url_list(url_list, inline_query):
        result = [
            InlineQueryResultPhoto(
                id=f"photo{i}-{InlineBaseBert.gen_id(url_list)}",
                photo_url=url,
                title=title,
                caption=desc,
                thumb_url=url
            )
            for i, (url, title, desc) in enumerate(url_list)
        ]

        InlineBaseBert._inl_send(result, inline_query)

    def inline_answer_gif_url(self, url, title="", caption=""):
        self.inline_answer_gif_urls([(url, title, caption)])

    def inline_answer_gif_urls(self, url_list):
        InlineBaseBert._inl_send_gif_url_list(url_list, self.inline_query)

    @staticmethod
    def _inl_send_gif_url_list(url_list, inline_query):
        result = [
            InlineQueryResultGif(
                id=f"gif{i}-{InlineBaseBert.gen_id(url_list)}",
                gif_url=url,
                title=title,
                caption=desc,
                thumb_url=url
            )
            for i, (url, title, desc) in enumerate(url_list)
        ]

        InlineBaseBert._inl_send(result, inline_query)

    @staticmethod
    def gen_id(array):
        return hashlib.md5(arr_to_bytes(array))

    @staticmethod
    def _inl_send(result, inline_query):
        try:
            inline_query.answer(result)
        except telegram.error.BadRequest:
            # took too long to answer
            pass


class ImageBaseBert(BaseBert):
    @staticmethod
    def pil_image_to_fp(image, img_format):
        fp = BytesIO()
        image.save(fp, img_format)
        fp.seek(0)
        return fp

    def send_pil_image(self, image, *, img_format='PNG', full=False, **kwargs):
        fp = ImageBaseBert.pil_image_to_fp(image, img_format)
        if full:
            return self.bot.send_document(self.chat_id, document=fp)

        return self.bot.send_photo(self.chat_id, fp, **kwargs)
