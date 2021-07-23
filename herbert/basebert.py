"""
Provides the BaseBert class

Classes inheriting BaseBert are used both
as a namespace to group related command
handlers, and as a context object that is
installed as part of the command handling,
such that a command handler can call
self.reply_text() without needing extra
information about the invocation context
and whether the call was via a chat command
or an inline handler
"""

import inspect
from io import BytesIO
from typing import Callable, Any

from common import chatformat
from common.reply import send_message as default_send
from common.reply_data import (
    File, Gif, Photo, PhotoUrl, Sticker, Text, ReplyData,
    ChatContext, InlineContext, Context
)


__all__ = ['BaseBert', 'ImageBaseBert']


class BaseBert:
    """
    BaseBert
    All command handlers are methods
    of classes inheriting this class

    Provides general methods to answer
    command invocations
    """
    def __init__(self, backend: Callable[[ReplyData, Context], Any] = default_send):
        self.context = None
        self._backend = backend

    def enumerate_cmds(self):
        return filter(lambda m: hasattr(m, 'cmdinfo'), self.enumerate_members())

    def enumerate_members(self):
        return map(lambda m: m[1], inspect.getmembers(self, inspect.ismethod))

    @property
    def message(self):
        """
        retrieve a message object, if that is
        available in the current context
        """
        if isinstance(self.context, ChatContext):
            return self.context.message

        # if isinstance(self.context, CallbackContext):
        #     return self.context.query.message
        return None

    @property
    def message_text(self):
        """
        if there is a message object associated
        with the current context, return its
        message text. Otherwise, if the context
        is from an inline query, return the query
        text
        """
        if self.message:
            return self.message.text

        if isinstance(self.context, InlineContext):
            return self.context.query.query

        return ""

    @property
    def chat_id(self):
        """
        if there is a message object associated
        with the current context, return its
        chat_id
        """
        return self.message and self.message.chat_id

    def send(self, obj: ReplyData):
        """
        Forward data to backend
        """
        if self.context is not None:
            return self._backend(obj, self.context)

    def send_message(self, msg, parse_mode=chatformat.get_parse_mode(),
                     disable_web_page_preview=False):
        """
        Send text to the user
        :param msg: A utf-8 encoded string to be sent
        :param parse_mode: One of the Styles defined in common.chatformat; states how formatting is expressed in msg
        :param disable_web_page_preview: set whether telegram should show the user a preview or not
        :return: a telegram.Message object on success
        """
        return self.send(self._prepare_text(msg, parse_mode, disable_web_page_preview))

    def send_sticker(self, sticker):
        return self.send(Sticker(sticker))

    def send_photo_from_file(self, path, caption=None, **kwargs):
        """ load a photo from a path and send it """
        assert len(kwargs) == 0
        with open(path, 'rb'):
            return self.send(Photo(caption, path))

    def send_file(self, fname, data, caption=None):
        """ send a binary file """
        return self.send(File(caption, data, fname))

    def send_text_file(self, msg, fname="message.txt", caption=None):
        """ send a text file """
        return self.send(File(caption, bytes(msg, encoding="UTF-8"), fname))

    def send_photo(self, data, caption=None):
        """ send an in-memory photo """
        return self.send(Photo(caption, data))

    # reply_ methods were a unified way to respond
    # both @inline and /directly.
    # since all methods support this now if available,
    # these are for backwards compatability
    def reply_text(self, string, **kwargs):
        return self.send_message(string, **kwargs)

    def reply_photo_url(self, url, caption=None):
        return self.send(PhotoUrl(caption, url))

    def reply_gif_url(self, url, caption=None):
        return self.send(Gif(caption, url))

    @staticmethod
    def _prepare_text(msg, parse_mode, disable_web_page_preview):
        return Text(*chatformat.parse_entities(msg, parse_mode),
                    disable_web_page_preview=disable_web_page_preview)


class ImageBaseBert(BaseBert):
    """
    Add some functions to basebert that
    are helpful for image handling
    """
    @staticmethod
    def pil_image_to_fp(image, img_format):
        """ convert a pil-image to a file-like object """
        file_like = BytesIO()
        image.save(file_like, img_format)
        file_like.seek(0)
        return file_like

    def send_pil_image(self, image, *a, img_format='PNG', full=False, caption=None,
                       disable_web_page_preview=False, parse_mode=None, **kwargs):
        """ send a pil image by converting it to a file object, then sending that """
        assert len(kwargs) == 0 and len(a) == 0
        file_like = ImageBaseBert.pil_image_to_fp(image, img_format)
        if isinstance(caption, str):
            caption = self._prepare_text(caption, parse_mode, disable_web_page_preview)
        return self.send(
            File(caption, file_like, 'image.png') if full else
            Photo(caption, file_like))
