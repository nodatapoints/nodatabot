from io import BytesIO

__all__ = ['Herberror', 'BaseBert', 'ImageBaseBert']


class Herberror(Exception):
    """Basic Herbert error"""


class BaseBert:
    def __init__(self):
        self.bot = None
        self.update = None

    @property
    def message(self):
        return self.update.message or self.update.callback_query.message

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

    @staticmethod
    def wrap_in_file(data, fname):
        f = BytesIO(data)
        f.name = fname
        return f


class ImageBaseBert(BaseBert):
    @staticmethod
    def pil_image_to_fp(image, format):
        fp = BytesIO()
        image.save(fp, format)
        fp.seek(0)
        return fp

    def send_pil_image(self, image, *, format='PNG', full=False, **kwargs):
        fp = ImageBaseBert.pil_image_to_fp(image, format)
        if full:
            return self.bot.send_document(self.chat_id, document=fp)

        return self.bot.send_photo(self.chat_id, fp, **kwargs)
