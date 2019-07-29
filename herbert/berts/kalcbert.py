import json
from PIL import Image
from io import BytesIO

from ext.sly import Lexer, Parser
import math
import pprint
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


class MathError(Herberror):
    pass


class MathSyntaxError(MathError):
    def __repr__(self):
        return f"Syntax Error:\n{super}"


class MathRangeError(MathError):
    def __repr__(self):
        return f"Range Error:\n{super}"


class MathValueError(MathError):
    def __repr__(self):
        return f"Value Error:\n{super}"


DEFAULT_NAMES = {
    'pi': math.pi,
    'e': math.e
}

DEFAULT_FUNCTIONS = {
    'sin': math.sin,
    'cos': math.cos,
    'ceil': math.ceil,
    'floor': math.floor,
    'int': math.trunc
}


# noinspection PyUnboundLocalVariable
class MathLexer(Lexer):
    tokens = {NAME, NUMBER, EXP, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, LPAREN, RPAREN, SEMI}
    ignore = ' \t\n'

    # Tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+(\.\d+)?(e\d*(\.\d*)?)?'

    # Special symbols
    EXP = r'\^'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    SEMI = r';'

    def error(self, t):
        raise MathSyntaxError("Illegal character '%s'\n" % t.value[0])


class MathParser(Parser):
    tokens = MathLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', EXP),
        ('right', UMINUS)
    )

    def __init__(self):
        self.names = DEFAULT_NAMES.copy()
        self.functions = DEFAULT_FUNCTIONS.copy()

    @_('NAME ASSIGN expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    @_('expr')
    def statement(self, p):
        return p.expr

    @_('statement SEMI statement')
    def statement(self, p):
        res = ()
        for s in (p.statement0, p.statement1):
            if s is not None:
                res += s if isinstance(s, tuple) else (s,)
        return res if len(res) > 0 else None

    @_('expr EXP expr')
    def expr(self, p):
        if abs(p.expr1) > 100:
            # raise MathRangeError(f"Exponent {p.expr1} is too large.")
            try:
                if p.expr1 > 0:
                    if -1 < p.expr0 < 1:
                        return 0
                    if p.expr0 == 1:
                        return 1
                    if p.expr0 > 1:
                        return float('inf')
                    return float('nan')
                else:
                    if p.expr0 <= 0:
                        return float('nan')
                    if p.expr0 < 1:
                        return float('inf')
                    if p.expr0 == 1:
                        return 1
                    return 0
            except TypeError:
                raise MathRangeError(
                    f"Ey um zu 'große' komplexe exponenten kannst du dich selber kümmern (was auch immer das heißt)")

        return p.expr0 ** p.expr1

    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        if p.expr1 == 0:
            return float('NaN')
            # raise MathRangeError(f"What do you {chatformat.italic('think')} dividing by 0 is supposed to mean??")
        return p.expr0 / p.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NAME LPAREN expr RPAREN')
    def expr(self, p):
        return self.functions[p.NAME](p.expr)

    @_('NUMBER')
    def expr(self, p):
        return float(p.NUMBER)

    @_('NAME')
    def expr(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            raise MathValueError(f'Undefined name {p.NAME!r}\n')

    def error(self, token):
        if token:
            raise MathSyntaxError(f'Failed at token {token.type}: "{token.value}"')
        else:
            raise MathSyntaxError(f'Failed: Unexpected end of input (Empty token list)')


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

        This supports basic operations (m§+§, m§-§, m§*§, m§/§, m§^§), variable assignments \
        (m§x = 5§), variable usage (m§3 + x§), and some function calls (m§sin(3e5)§).
        
        Example:
        m§/math
        x = 5
        y = 10
        z = x * (y^x)
        
        z / (x^y)
        1 + z
        z^0.5§
        """
    )
    def math(self, string):
        lex = MathLexer()
        parse = MathParser()
        printed_something = False

        string = string.strip()
        if string == '':
            raise Herberror("Empty input :(")

        for line in string.split('\n'):
            line = line.strip()
            if line == '':
                continue

            result = parse.parse(lex.tokenize(line))
            if result is not None:
                printed_something = True
                self.reply_text(str(result))

        if not printed_something:
            res_str = "".join(f"\'{var}\': {val}\n" for var, val in parse.names.items())
            self.reply_text(chatformat.mono(res_str))

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
            _, data = load_content(url)  # ^^^ buffers
            image = Image.open(BytesIO(data))  # so i need to force a new download
            # image = Image.new('RGB', (500, 500))
            link, _ = chatformat.render(chatformat.link_to(url, "David Kriesel"), chatformat.STYLE_BACKEND)
            self.send_pil_image(image, caption="Data and plots scraped from the website of " + link,
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
                num_of_hash = int(percent / 100 * n + 0.5)
                percentnum = str(percent) + "% "
                percentnum_length = len(percentnum)

                string = '#' * num_of_hash + ' ' * (n - num_of_hash - percentnum_length) + percentnum
                return string

            output = f"Poll for {name}\nTaken around {date}\n\n"
            for key, result in results.items():
                output += f"{PartyIdtoName[int(key)]} |{fillHash(35, result)}|\n"

            output = chatformat.mono(output)
            self.reply_text(output)

    @command(pass_args=False, register_help=False, allow_inline=True)
    def rng(self):
        self.reply_text("4")  # chosen by fair dice roll
        pass  # guaranteed to be random
