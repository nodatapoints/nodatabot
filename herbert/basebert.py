from io import BytesIO

__all__ = ['Herberror', 'BaseBert']


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

    @staticmethod
    def pil_image_to_fp(image, format):
        fp = BytesIO()
        image.save(fp, format)
        fp.seek(0)
        return fp

    def send_message(self, *args, **kwargs):
        return self.bot.send_message(self.chat_id, *args, **kwargs)

    def send_pil_image(self, image, *, format='PNG', full=False, **kwargs):
        fp = self.pil_image_to_fp(image, format)
        if full:
            return self.bot.send_document(self.chat_id, document=fp)

        return self.bot.send_photo(self.chat_id, fp, **kwargs)
