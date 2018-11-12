from io import BytesIO
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
import hashlib
from common.basic_utils import arr_to_bytes

__all__ = ['Herberror', 'BaseBert', 'ImageBaseBert', 'InlineBaseBert']


class Herberror(Exception):
    """Basic Herbert error"""


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

    def send_message(self, *args, parse_mode='MARKDOWN', **kwargs):
        return self.bot.send_message(
            self.chat_id,
            *args,
            parse_mode=parse_mode,
            **kwargs
        )

    def send_photo_from_file(self, path, **kwargs):
        return self.bot.send_photo(self.chat_id, open(path, 'rb'), **kwargs)

    def send_file(self, fname, data, **kwargs):
        from common import chat
        chat.t_reply_filed_binary(self.bot, self.update, data, name=fname, **kwargs)

    def send_photo(self, data, **kwargs):
        self.bot.send_photo(self.chat_id, data, **kwargs)

    # reply_ methods are a unified way to respond
    # both @inline and /directly.
    def reply_str(self, string):
        if self.inline:
            InlineBaseBert._inl_send_str_list([string], self.inline_query)
        else:
            self.send_message(string)

    def reply_photo_url(self, url, title="", caption=""):
        if self.inline:
            InlineBaseBert._inl_send_photo_url_list([(url, title, caption)], self.inline_query)
        else:
            self.send_photo(url, title=title, caption=caption)

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
                title=string,
                input_message_content=InputTextMessageContent(string)
            )
            for i, string in enumerate(str_list)
        ]

        inline_query.answer(result)

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

        inline_query.answer(result)

    @staticmethod
    def gen_id(array):
        return hashlib.md5(arr_to_bytes(array))


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
