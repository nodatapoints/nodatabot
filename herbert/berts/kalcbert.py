from PIL import Image
from io import BytesIO

from decorators import *
from basebert import ImageBaseBert, InlineBaseBert
from herberror import Herberror, BadHerberror
from common.network import load_content, load_str, get_url_safe_string
from common.argparser import Args

from common.chatformat import mono

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''


class KalcBert(InlineBaseBert, ImageBaseBert):
    @aliases('wttr')
    @command(allow_inline=True, pass_string=True)
    @doc(
        """
        Take a look at the weather all over the world (asciistyle)

        The weather utility uses the service provided by the "wttr.in" website \
        which gives you a weather forecast for any city around the world. \
        It gets displayed in an Ascii-format, so that very little data is needed.

        The default city is Greifswald, Germany (HGW), which is entirely unrelated to the authors usual location.
        You can also set the info attribute to 1 or 2 to get more tangential information.

        e.g: m§/wttr [info=1] New York§
        """
    )
    def weather(self, string):
        argvals, string = Args.parse(string, {
            'info': Args.T.INT,
        })

        info = argvals.get('info') or 0
        info = ('x' if info > 1 else 'q') if info > 0 else 'Q'

        string = string or 'Greifswald'
        wttr_string = load_str(
            f'wttr.in/{get_url_safe_string(string)}?T&M&0&{info}', fake_ua=False)
        if '=======' in wttr_string:  # good enough
            raise Herberror('No place with that name was found')

        self.reply_text(mono(wttr_string))

    @aliases('wa', 'wolframalpha')
    @command(pass_string=True)
    @doc(
        """
        Show a WolframAlpha generated informationsheet based on the given string

        The wolfram command gives you easy and comprehensive factual data about most topics. \
        Using the language processing and database access WolframAlpha API, it will send you an image \
        summarizing available data concerning your query. You can choose if you want the image as full file \
        or with Telegramcompression.

        e.g: m§/wolfram [send=file] plot Lemniscate§
        """
    )
    def wolfram(self, string):
        argvals, string = Args.parse(string, {
            'send': Args.T.one_of('img', 'file', 'both'),
        })
        arg_send = argvals.get('send') or 'img'

        query = get_url_safe_string(string)
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'

        if arg_send == 'file' or arg_send == 'both':  # high resolution file
            _, data = load_content(url)
            image = Image.open(BytesIO(data))
            self.bot.send_document(
                self.chat_id, document=ImageBaseBert.pil_image_to_fp(image, 'PNG'))
        if arg_send == 'img' or arg_send == 'both':  # not full  ->  simple image
            string = string if self.inline else ''
            self.reply_gif_url(url, caption=string, title='')

    """
    @aliases('stepbystep', 'sbs')
    @command(pass_string=True)
    def sbswolfram(self, string):
        "-"-"
        Show detailed step by step solutions for mathematical input problems
        The step by step wolfram command is specialized for mathematical processes.
        It presents the steps for the calculation or derivation of some kind of problem in an easy to follow format,
        with the special benefit that this isn't possible on the standard website.

        meh doesnt work, we need to get premium
        "-"-"
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
        datax = xdatax[(xdatax.find('Possible intermediate steps') + 44):]
        # delete xml artifacts and cut string at end of link
        data, *_ = datax.replace("&amp;", "&").split("'")
        # check if it worked and a url is found
        if data[:4] == "http":
            _, realdata = load_content(data)

            image = Image.open(BytesIO(realdata))
            self.send_pil_image(image, full=False)
        else:
            raise Herberror('no step by step solution feasible')
    """

    # new part
    @command(pass_string=True, allow_inline=True)
    @doc(
        """
        Evaluate a simple mathematical expression and return the result

        This is a simple calculator using python syntax to return results directly in the Telegram environment \
        to fit into the flow of the conversation. The spported Operators are brackets \
        and relational operators ( ==, !=, <, >, <=, >=) \
        as well as
        m$ + § Addition
        m$ - § Subtraction
        m$ * § Multiplication
        m$ / § Division
        m$ % § Modulus
        m$ **§ Exponentiation

        e.g: m§/math 365*(24-8)§
        """
    )
    def math(self, string):
        allowed_chars = set('1234567890.+*-/%=()<> ')
        if set(string).issubset(allowed_chars):
            try:
                self.reply_text(str(eval(string, {}, {})))
            except Exception:
                raise Herberror('not a working equation')
        else:
            raise Herberror('Only + - * / % ** are supported.')

    @command(pass_args=False, register_help=False, allow_inline=True)
    def rng(self):
        self.reply_text("4")     # chosen by fair dice roll
        pass                     # guaranteed to be random
