from functools import lru_cache
from urllib.parse import quote

from PIL import Image, ImageOps
from io import BytesIO

from decorators import command, aliases
from basebert import ImageBaseBert, Herberror
from common.hercurles_network import _t_load_content

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''

class KalcBert(ImageBaseBert):

    @aliases('wa', 'wolframalpha')
    @command(pass_string=True)
    def wolfram(self, string, full=False, steps=False):
        """
        Show a WolframAlpha generated informationsheet based on the given string
        """
        query = quote(string, safe='')
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'
        _, data = _t_load_content(url)

        image = Image.open(BytesIO(data))
        self.send_pil_image(image, full=full)

    @aliases('hrwa')
    @command(pass_string=True)
    def highreswolfram(self, string):
        """
        Send a high resolution WolframAlpha generated informationsheet based on the given string as a file
        """
        self.wolfram(string, full=True, steps=False)

    @command(pass_string=True)
    def math(self, string):
        """
        Evaluate a simple mathematical expression and return the result
        """
        allowed_chars = set('1234567890.+*-/%=()')
        if set(string).issubset(allowed_chars):
            try:
                self.send_message(eval(string, {}, {}))
            except Exception:
                raise Herberror('not a working equation')
        else: raise Herberror('Dude, NO arbitrary code exec')
