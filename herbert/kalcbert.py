from PIL import Image
from io import BytesIO

from decorators import *
from basebert import ImageBaseBert, Herberror, BadHerberror, InlineBaseBert
from common.network import load_content, load_str, get_url_safe_string
from common.argparser import Args

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''


class KalcBert(InlineBaseBert, ImageBaseBert):
    @aliases('wttr')
    @command(allow_inline=True, pass_string=True)
    def weather(self, string):
        """
        Take a look at the weather all over the world (asciistyle)

        The weather utility uses the service provided by the "wttr.in" website \
        which gives you a weather forecast for any city around the world. \
        It gets displayed in an Ascii-format, so that very little data is needed.

        The default city is Greifswald, Germany (HGW), which is entirely unrelated to the authors usual location.
        You can also set the info attribute to 1 or 2 to get more tangential information.

        e.g: `/wttr [info=1] New York`
        """
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

        self.reply_text(f'```{wttr_string}```')

    @aliases('wa', 'wolframalpha')
    @command(pass_string=True, allow_inline=True)
    def wolfram(self, string, full=False):
        """
        Show a WolframAlpha generated informationsheet based on the given string

        The wolfram command gives you easy and comprehensive factual data about most topics. \
        Using the language processing and database access WolframAlpha API, it will send you an image \
        summarizing available data concerning your query.

        e.g: `/wolfram plot Lemniscate`
        """
        query = get_url_safe_string(string)
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'

        if full and self.inline:
            raise BadHerberror('Should be unreachable')
        elif full:  # high resolution file
            _, data = load_content(url)
            image = Image.open(BytesIO(data))
            self.bot.send_document(self.chat_id, document=ImageBaseBert.pil_image_to_fp(image, 'PNG'))
        else:  # not full  ->  simple image
            string = string if self.inline else ''  
            self.reply_gif_url(url, caption=string, title='')

    @aliases('hrwa', 'hrwolfram')
    @command(pass_string=True)
    def highreswolfram(self, string):
        """
        Send a high resolution WolframAlpha generated informationsheet based on the given string as a file

        The highreswolfram command gives you easy and comprehensive factual data about most topics. \
        Using the language processing and database access WolframAlpha API, it will send you a higher \
        resolution png-file summarizing available data concerning your query.

        e.g: `/hrwolfram Lemniscate`
        """
        self.wolfram(string, full=True)

    """
    @aliases('stepbystep', 'sbs')
    @command(pass_string=True)
    def sbswolfram(self, string):
        "-"-"
        Show detailed step by step solutions for mathematical input problems
        The step by step wolfram command is specialized for mathematical processes.
        It presents the steps for the calculation or derivation of some kind of problem in an easy to follow format,
        with the special benefit that this isn't possible on the standard website.


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
    def math(self, string):
        """
        Evaluate a simple mathematical expression and return the result

        This is a simple calculator using python syntax to return results directly in the Telegram environment \
        to fit into the flow of the conversation. The spported Operators are brackets \
        and relational operators ( ==, !=, <, >, <=, >=) \
        as well as
        ` +  `Addition
        ` -  `Subtraction
        ` *  `Multiplication
        ` /  `Division
        ` %  `Modulus
        ` ** `Exponent

        e.g: `/math 365*(24-8)`
        """
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
