
from io import BytesIO


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

    @staticmethod
    def pil_image_to_fp(image, format):
        fp = BytesIO()
        image.save(fp, format)
        fp.seek(0)
        return fp

    def send_message(self, *args, **kwargs):
        self.bot.send_message(self.message.chat_id, *args, **kwargs)

    def send_pil_image(self, image, *, format='PNG', **kwargs):
        fp = self.pil_image_to_fp(format)
        return self.bot.send_photo(self.message.chat_id, fp, **kwargs)
