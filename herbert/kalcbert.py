from functools import lru_cache

from PIL import Image, ImageOps
from io import BytesIO

from decorators import command, aliases
from basebert import ImageBaseBert, Herberror
from common.network import t_load_content, t_load_str, _t_url_save_string

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''

class KalcBert(ImageBaseBert):
    @aliases('wttr')
    @command
    def weather(self, args):
        """
        Take a look at the weather all over the world (asciistyle)
        """
        if len(args) == 0: args = ['Greifswald']
        self.send_message('```'+t_load_str(f"wttr.in/{_t_url_save_string(args[0])}?T&q&0&n", fake_ua=False)+'```')

    @aliases('wa', 'wolframalpha')
    @command(pass_string=True)
    def wolfram(self, string, full=False):
        """
        Show a WolframAlpha generated informationsheet based on the given string
        """
        query = _t_url_save_string(string)
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'
        _, data = t_load_content(url)

        image = Image.open(BytesIO(data))
        self.send_pil_image(image, full=full)

    @aliases('hrwa')
    @command(pass_string=True)
    def highreswolfram(self, string):
        """
        Send a high resolution WolframAlpha generated informationsheet based on the given string as a file
        """
        self.wolfram(string, full=True)

    @aliases('stepbystep', 'sbs')
    @command(pass_string=True)
    def sbswolfram(self, string):
        """
        Show detailed step by step solutions for mathematical input problems
        """
        # higly susceptible to fails if WolframAlphas output xml changes
        # but no scrapy so usable in python 3.7
        query = _t_url_save_string(string)
        url = f'http://api.wolframalpha.com/v2/query?appid=36GXXR-K5UA8L8XTY&input={query}&podstate=Step-by-step%20solution&format=image'
        _, xdatax = t_load_content(url) # XML website
        xdatax = str(xdatax)
        # check if it worked
        # find unique point in String relating to the giflink and go on from there to start of link [magic number 44] later
        # cut string at start of link
        datax = xdatax[(xdatax.find('Possible intermediate steps')+44):] 
        # delete xml artifacts and cut string at end of link
        data, *_ = datax.replace("&amp;", "&").split("'")
        # check if it worked and a url is found
        if data[:4] == "http":
            _, realdata = t_load_content(data)

            image = Image.open(BytesIO(realdata))
            self.send_pil_image(image, full=False)
        else:
            raise Herberror('no step by step solution feasible')


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

    @command(pass_args=False, register_help=False)
    def rng(self):
        self.send_message("4") # chosen by fair dice roll
                               # guaranteed to be random

