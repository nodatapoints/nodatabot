import json
from PIL import Image
from io import BytesIO

from decorators import *
from basebert import ImageBaseBert, InlineBaseBert
from herberror import Herberror, BadHerberror
from common.network import load_content, load_str, get_url_safe_string
from common.argparser import Args

from common import chatformat

'''
Meine Datei zum berechenen/bearbeiten von queries
- Philip
'''

StateCodeToId = {
    "ger": 0, "bw": 1, "bay": 2, "be": 3,
    "brb": 4, "bre": 5, "hh": 6, "he": 7,
    "mv": 8, "ns": 9, "nrw": 10, "rp": 11,
    "srl": 12, "sa": 13, "saa": 14,
    "sh": 15, "th": 16
}

PartyIdtoName = {
    0: "Sonstig",
    1: "  Union",
    2: "    SPD",
    3: "    FDP",
    4: "  Grüne",
    5: "  Linke",
    6: "Piraten",
    7: "    AfD",
    8: "Freie W",
    10: "    SSW",
    13: "DPARTEI",
    14: " BVB/FW",
    15: "Tiersch",
    16: "    BIW",
    101: "    CDU",
    102: "    CSU"
}


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

        self.reply_text(chatformat.mono(wttr_string))

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

    @aliases('polit', 'pltc')
    @command(pass_string=True)
    @doc(
        f"""
        Take a quick look at german polls

        The politic utility uses "dawum" and David Kriesels live viewer to show you the \
        most recent public politic opinion of every state. For germany as a whole, you also have the option \
        to take a look at how public opinion fluctuated by using m§[len=90 (/last/all)]§.
        More Information on {chatformat.link_to("https://dawum.de/Ueber_uns/", "dawum")} and\
        {chatformat.link_to("http://www.dkriesel.com/", "dkriesel")}.
        States you can use in the command (m§GER§ is the standard):
        i§BW, Bay, Be, BrB, Bre, HH, He, MV, NS, NRW, RP, SrL, Sa, SaA, SH, Th, GER§

        e.g: m§/politic [len=all]§
        e.g: m§/politic MV§
        """
    )
    def politic(self, string):
        schland = StateCodeToId["ger"]
        argvals, string = Args.parse(string, {
            'len': Args.T.one_of("all", "last", "90"),
        })
        length = argvals.get('len') or ''
        state = StateCodeToId.get(string.lower(), schland)

        if state == schland and length:
            # dkriesel timelines
            substitution = {"all": "all", "last": "wahl2017", "90": "90tage"}
            choice = substitution.get(length, substitution["90"])
            url = f"www.dkriesel.com/_media/sonntagsfrage_{choice}.png"

            # self.reply_photo_url(url, caption="kapollo")
            _, data = load_content(url)         # ^^^ buffers
            image = Image.open(BytesIO(data))   # so i need to force a new download
            # image = Image.new('RGB', (500, 500))
            link, _ = chatformat.render(chatformat.link_to(url, "David Kriesel"), chatformat.STYLE_BACKEND)
            self.send_pil_image(image, caption="Data and plots scraped from the website of "+link,
                                parse_mode='HTML', disable_web_page_preview=True)

        else:
            # dawum image needs to be loaded
            url = "https://api.dawum.de/newest_surveys.json"
            data_type, json_data = load_content(url)
            if data_type != "application/json":
                print(data_type)
                raise BadHerberror('Poll data format changed, please contact an adminstrator')

            data = json.loads(json_data)

            small_string = string.strip().lower()

            code = StateCodeToId.get(small_string)
            if code is None:
                raise Herberror("not a supported state code")
            name = data["Parliaments"][str(code)]["Name"]
            # those are ordered, so I can iterate
            for poll_key, poll_data in data["Surveys"].items():
                if int(poll_data['Parliament_ID']) == code:
                    results = poll_data["Results"]
                    date = poll_data["Date"]
                    break

            # generate the bars dependent on the percentages
            def fillHash(n, percent):
                num_of_hash = int(percent/100*n + 0.5)
                percentnum = str(percent) + "% "
                percentnum_length = len(percentnum)

                string = '#'*num_of_hash + ' '*(n-num_of_hash-percentnum_length) + percentnum
                return string

            output = f"Poll for {name}\nTaken around {date}\n\n"
            for key, result in results.items():
                output += f"{PartyIdtoName[int(key)]} |{fillHash(35, result)}|\n"

            output = chatformat.mono(output)
            self.reply_text(output)

    @command(pass_args=False, register_help=False, allow_inline=True)
    def rng(self):
        self.reply_text("4")     # chosen by fair dice roll
        pass                     # guaranteed to be random
