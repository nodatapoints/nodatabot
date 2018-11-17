from PIL import Image
from io import BytesIO

from decorators import *
from basebert import ImageBaseBert, Herberror, InlineBaseBert
from common.network import load_content, load_str, get_url_safe_string

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''


class KalcBert(InlineBaseBert, ImageBaseBert):
    @aliases('wttr')
    @command(allow_inline=True)
    def weather(self, args):
        """
        Take a look at the weather all over the world (asciistyle)
        """
        args = args or ('Greifswald', )
        wttr_string = load_str(f'wttr.in/{get_url_safe_string(args[0])}?T&q&0&n', fake_ua=False)
        self.reply_str(f'```{wttr_string}```', args[0])

    @aliases('wa', 'wolframalpha')
    @command(pass_string=True, allow_inline=True)
    def wolfram(self, string, full=False):
        """
        Show a WolframAlpha generated informationsheet based on the given string
        """
        query = get_url_safe_string(string)
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'
        
        ###
        ### TODO GIF INLINE SUPPORT
        ###
        if full or not full: 
            # high resolution file
            _, data = load_content(url)
            image = Image.open(BytesIO(data))
            self.send_pil_image(image, full=full)
        else:
            # simple image
            self.reply_photo_url(
                url, caption='caption', title='title'
            )


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
        query = get_url_safe_string(string)
        url = f'http://api.wolframalpha.com/v2/query?appid=36GXXR-K5UA8L8XTY&input={query}&podstate=Step-by-step%20solution&format=image'
        _, xdatax = load_content(url)  # XML website
        xdatax = str(xdatax)
        # check if it worked
        # find unique point in String relating to the giflink
        # and go on from there to start of link [magic number 44] later
        # cut string at start of link
        datax = xdatax[(xdatax.find('Possible intermediate steps')+44):]
        # delete xml artifacts and cut string at end of link
        data, *_ = datax.replace("&amp;", "&").split("'")
        # check if it worked and a url is found
        if data[:4] == "http":
            _, realdata = load_content(data)

            image = Image.open(BytesIO(realdata))
            self.send_pil_image(image, full=False)
        else:
            raise Herberror('no step by step solution feasible')

    @command(pass_string=True, allow_inline=True)
    def math(self, string):
        """
        Evaluate a simple mathematical expression and return the result
        """
        allowed_chars = set('1234567890.+*-/%=() ')
        if set(string).issubset(allowed_chars):
            try:
                self.reply_str(str(eval(string, {}, {})))
            except Exception:
                raise Herberror('not a working equation')
        else:
            raise Herberror('Dude, NO arbitrary code exec')

    @command(pass_args=False, register_help=False, allow_inline=True)
    def rng(self):
        self.reply_str("4")     # chosen by fair dice roll
        pass                    # guaranteed to be random
