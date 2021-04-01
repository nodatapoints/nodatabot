import json
import math
import operator
from io import BytesIO
from abc import ABC, abstractmethod
from typing import Dict, Union, Callable
from enum import Enum

from PIL import Image

from ext.sly import Lexer, Parser
from decorators import aliases, command, doc
from basebert import ImageBaseBert, InlineBaseBert
from herberror import Herberror, BadHerberror
from common.network import load_content, load_str, get_url_safe_string
from common.argparser import Args
from common import chatformat

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


class UnitClass(Enum):
    LENGTH, TIME, MASS = range(3)


def _dict_strip_zeroes(dct):
    return {k: v for k, v in dct.items() if v != 0}


class Unit:
    """
    Represent the dimension and prescaling of a quantity
    """
    def __init__(self, dim: Dict[UnitClass, float], factor: float, allow_prefixing=False):
        self.dim, self.factor, self.allow_prefixing = dim, factor, allow_prefixing

    def conversion_factor(self, other):
        """
        Calculate the relative prescaling between two
        unit objects
        """
        if self.dim != other.dim:
            raise MathValueError('Adding or Subtracting non-matching units')
        return other.factor / self.factor

    def __eq__(self, other):
        return _dict_strip_zeroes(self.dim) == _dict_strip_zeroes(other.dim)

    def __mul__(self, other):
        dim = self.dim.copy()
        for k, val in other.dim.items():
            dim[k] = dim.get(k, 0) + val
        return Unit(dim, self.factor * other.factor)

    def __truediv__(self, other):
        dim = self.dim.copy()
        for k, val in other.dim.items():
            dim[k] = dim.get(k, 0) - val
        return Unit(dim, self.factor / other.factor)

    def __pow__(self, exp):
        return Unit({k: exp * v for k, v in self.dim.items()}, self.factor ** exp)


no_unit = Unit(dict(), 1)
UC = UnitClass

# this should ideally be a multimap<UnitDimension, UnitFamily>
# where UnitDimension describes the exponents for each UnitClass (e.g. LENGTH: 1)
# and UnitFamily describes basename (e.g. 'm') or basenames (e.g. m^3 and l),
# which prefixes are allowed and which version is to be used as the default.
#
# I cannot be bothered, however, so this is an approximation and hektowatt and
# kiloliter are a thing now (and some code is uglier than it needed to be)
units = {
    'm': Unit({UC.LENGTH: 1}, 1, True),
    'g': Unit({UC.MASS: 1}, 1000, True),
    's': Unit({UC.TIME: 1}, 1),
    'N': Unit({UC.MASS: 1, UC.LENGTH: 1, UC.TIME: -2}, 1, True),
    'Hz': Unit({UC.TIME: -1}, 1, True),
    'J': Unit({UC.MASS: 1, UC.LENGTH: 2, UC.TIME: -2}, 1, True),
    'W': Unit({UC.MASS: 1, UC.LENGTH: 2, UC.TIME: -3}, 1, True),
    'l': Unit({UC.LENGTH: 3}, 1000, True)
}


class PrefixHandler:
    """
    Parse unit size prefixes
    """
    _prefixes = {
        'a': 10 ** 18,
        'f': 10 ** 15,
        'p': 10 ** 12,
        'n': 10 ** 9,
        'u': 10 ** 6,
        'm': 10 ** 3,
        'c': 10 ** 2,
        'd': 10,
        # identity
        # 10^-1
        'h': 10 ** -2,
        'k': 10 ** -3,
        'M': 10 ** -6,
        'G': 10 ** -9,
        'T': 10 ** -12
    }

    _str_for_unit_class = {
        UnitClass.LENGTH: 'm',
        UnitClass.MASS: 'kg',
        UnitClass.TIME: 's'
    }

    @staticmethod
    def decode_name(namestr) -> Unit:
        """
        Calculate a unit object from a string
        """
        if namestr in units:
            return units[namestr]

        if namestr == '1':
            return no_unit

        if namestr[0] in PrefixHandler._prefixes and namestr[1:] in units:
            base = units[namestr[1:]]
            fact = PrefixHandler._prefixes[namestr[0]]
            if base.allow_prefixing:
                return Unit(base.dim, base.factor * fact)

        raise MathValueError(f'Unknown unit {namestr!r}')

    @staticmethod
    def encode_value(value) -> str:
        """
        Represent a value as a string, using
        a proper size prefix
        """
        abs_val, unit = value.absolute, value.unit
        if unit == no_unit:
            return str(abs_val / unit.factor)

        unit_type = PrefixHandler._find_unit(unit.dim)
        if unit_type is not None:
            name, base_unit = unit_type
            val, prefix = abs_val * unit.conversion_factor(base_unit), ''
            if base_unit.allow_prefixing:
                val, prefix = PrefixHandler.find_fitting_prefix(val)
            return str(val) + f'_{prefix}{name}'

        return str(abs_val / unit.factor) + PrefixHandler._format_dimension(unit.dim)

    @staticmethod
    def find_fitting_prefix(val):
        """
        Find the closest appropriate size prefix for a floating
        point value
        """
        ok_k = ''
        ok_v = 1
        for k, factor in PrefixHandler._prefixes.items():
            scaling = 1 / factor
            if 1 <= ok_v <= scaling <= val or 1 >= ok_v >= scaling >= val:
                ok_k, ok_v = k, scaling
        return val / ok_v, ok_k

    @staticmethod
    def _format_dimension(dim):
        pos = "*".join(PrefixHandler._str_for_unit_class[k] +
                       (f'^{v}' if v > 1 else '') for k, v in dim.items() if v > 0)
        neg = "*".join(PrefixHandler._str_for_unit_class[k] +
                       (f'^{-v}' if v < -1 else '') for k, v in dim.items() if v < 0)
        return '_' + (pos if pos else '1') + (f'/({neg})' if neg else '')

    @staticmethod
    def _find_unit(dim):
        for name, unit in units.items():
            if unit.dim == dim:
                return name, unit
        return None


class Value:
    def __init__(self, absolute: float, unit: Unit = no_unit):
        self.absolute, self.unit = absolute, unit

    def __add__(self, other):
        return Value(self.absolute + other.absolute * other.unit.conversion_factor(self.unit), self.unit)

    def __sub__(self, other):
        return Value(self.absolute - other.absolute * other.unit.conversion_factor(self.unit), self.unit)

    def __mul__(self, other):
        return Value(self.absolute * other.absolute, self.unit * other.unit)

    def __truediv__(self, other):
        res_abs = self.absolute / other.absolute if other.absolute != 0 else float('NaN')
        return Value(res_abs, self.unit / other.unit)

    def __neg__(self):
        return Value(-self.absolute, self.unit)

    def __pow__(self, exp):
        if exp.unit.dim:
            raise MathValueError('Cannot use units in exponents (yet)')
        val1, val2 = self.absolute, exp.absolute

        if abs(val2) > 100:
            try:
                res = 0

                if val2 > 0:
                    if -1 < val1 < 1:
                        res = Value(0)
                    elif val1 == 1:
                        res = Value(1)
                    elif val1 > 1:
                        res = Value(float('inf'))
                    else:
                        res = Value(float('nan'))
                else:
                    if val1 <= 0:
                        res = Value(float('nan'))
                    elif val1 < 1:
                        res = Value(float('inf'))
                    elif val1 == 1:
                        res = Value(1)
                    else:
                        res = Value(0)

                return res

            except TypeError:
                raise MathRangeError(
                    "Ey um zu 'große' komplexe exponenten kannst du dich selber kümmern (was auch immer das heißt)") from None

        return Value(val1 ** val2, self.unit ** val2)

    def __str__(self):
        return PrefixHandler.encode_value(self)

    def __repr__(self):
        return str(self)


class ASTNode(ABC):
    def evaluate(self, names):
        return self.get_functor()(names)

    @abstractmethod
    def get_functor(self):
        raise NotImplementedError()


class Constant(ASTNode):
    def __init__(self, valstr, unitstr='_1'):
        self.value = Value(float(valstr), PrefixHandler.decode_name(unitstr[1:]))

    def get_functor(self):
        return lambda _: self.value


def _get(items, name, expected_type, tpn):
    if name not in items:
        raise MathValueError(f'Undefined {tpn} {name!r}')
    val = items[name]
    if not isinstance(val, expected_type):
        raise MathValueError(f'Object {name!r} is of invalid type (expected {tpn!r})')
    return val


class VariableLookup(ASTNode):
    def __init__(self, var_name):
        self.var_name = var_name

    def get_functor(self):
        return lambda names: _get(names, self.var_name, Value, 'variable')


class FunctionInvocation(ASTNode):
    def __init__(self, fn_name, arg: ASTNode):
        self.fn_name = fn_name
        self.arg = arg

    def get_functor(self):
        return lambda names: _get(names, self.fn_name, Callable, 'function')(self.arg.evaluate(names))


class FunctionExpressionWrapper:
    def __init__(self, fun, names, *arg_names):
        self.fun, self.names, self.arg_names = fun, names.copy(), arg_names

    def __call__(self, *args):
        names = self.names
        names.update(dict(zip(self.arg_names, args)))
        return self.fun(self.names)


def _make_bin_op(bin_op):
    """
    auto-generate AST classes for binary operators
    """

    class _C(ASTNode):
        def __init__(self, lhs: ASTNode, rhs: ASTNode):
            self.bin_op, self.lhs, self.rhs = bin_op, lhs, rhs

        def get_functor(self):
            return lambda arg_dict: self.bin_op(self.lhs.evaluate(arg_dict),
                                                self.rhs.evaluate(arg_dict))

    return _C


Product = _make_bin_op(operator.mul)
Sum = _make_bin_op(operator.add)
Difference = _make_bin_op(operator.sub)
Quotient = _make_bin_op(operator.truediv)
Power = _make_bin_op(operator.pow)


class Negate(ASTNode):
    def __init__(self, val: ASTNode):
        self.val = val

    def get_functor(self):
        return lambda names: -self.val.evaluate(names)


DEFAULT_NAMES: Dict[str, Union[Value, Callable, FunctionExpressionWrapper]] = {
    'pi': Value(math.pi),
    'e': Value(math.e),
    'sin': math.sin,
    'cos': math.cos,
    'ceil': math.ceil,
    'floor': math.floor,
    'int': math.trunc,
    'c': Value(299792485, Unit({UC.LENGTH: 1, UC.TIME: -1}, 1))
}


# noinspection PyUnboundLocalVariable
class MathLexer(Lexer):
    # pylint: disable = E, W, R, C
    # (pylint doesnt get what sly is doing)
    tokens = {NAME, NUMBER, DEF, EXP, PLUS, TIMES, MINUS, DIVIDE, FASSIGN, ASSIGN, LPAREN, RPAREN, SEMI, UNIT}
    ignore = ' \t\n'

    # Tokens
    DEF = r'def'
    UNIT = r'_[a-zA-Z][a-zA-Z]*'
    NAME = r'[a-zA-Z][a-zA-Z0-9_]*'
    NUMBER = r'\d+(\.\d+)?(e\d*(\.\d*)?)?'

    # Special symbols
    EXP = r'\^'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    FASSIGN = r':='
    ASSIGN = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    SEMI = r';'

    def error(self, t):
        raise MathSyntaxError("Illegal character '%s'" % t.value[0])


class MathParser(Parser):
    # pylint: disable = E, W, R, C
    tokens = MathLexer.tokens

    precedence = (
        ('left', SEMI),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', EXP),
        ('right', UMINUS)
    )

    def __init__(self):
        self.names = DEFAULT_NAMES.copy()

    @_('NAME ASSIGN expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr.evaluate(self.names)

    @_('expr')
    def statement(self, p):
        return p.expr.evaluate(self.names)

    @_('function_expr ASSIGN expr')
    def statement(self, p):
        name, arg = p.function_expr
        if not isinstance(arg, VariableLookup):
            raise MathValueError('Invalid function definition')
        self.names[name] = FunctionExpressionWrapper(p.expr.get_functor(), self.names, arg.var_name)

    @_('statement SEMI statement')
    def statement(self, p):
        res = ()
        for s in (p.statement0, p.statement1):
            if s is not None:
                res += s if isinstance(s, tuple) else (s,)
        if len(res) <= 0:
            return None
        elif len(res) == 1:
            return res[0]
        else:
            return res

    @_('expr EXP expr')
    def expr(self, p):
        return Power(p.expr0, p.expr1)

    @_('expr PLUS expr')
    def expr(self, p):
        return Sum(p.expr0, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return Difference(p.expr0, p.expr1)

    @_('expr TIMES expr')
    def expr(self, p):
        return Product(p.expr0, p.expr1)

    @_('expr DIVIDE expr')
    def expr(self, p):
        return Quotient(p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return Negate(p.expr)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('function_expr')
    def expr(self, p):
        return FunctionInvocation(*p.function_expr)

    @_('NUMBER UNIT')
    def expr(self, p):
        return Constant(p.NUMBER, p.UNIT)

    @_('NUMBER')
    def expr(self, p):
        return Constant(p.NUMBER)

    @_('UNIT')
    def expr(self, p):
        return Constant(1, p.UNIT)

    @_('NAME')
    def expr(self, p):
        return VariableLookup(p.NAME)

    @_('NAME LPAREN expr RPAREN')
    def function_expr(self, p):
        return p.NAME, p.expr

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

        if arg_send in ('file', 'both'):  # high resolution file
            _, data = load_content(url)
            image = Image.open(BytesIO(data))
            self.bot.send_document(
                self.chat_id, document=ImageBaseBert.pil_image_to_fp(image, 'PNG'))
        if arg_send in ('img', 'both'):  # not full  ->  simple image
            string = string if self.inline else ''
            self.reply_gif_url(url, caption=string, title='')

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
            for _, poll_data in data["Surveys"].items():
                if int(poll_data['Parliament_ID']) == code:
                    results = poll_data["Results"]
                    date = poll_data["Date"]
                    break

            # generate the bars dependent on the percentages
            def fill_hash(n, percent):
                num_of_hash = int(percent / 100 * n + 0.5)
                percentnum = str(percent) + "% "
                percentnum_length = len(percentnum)

                string = '#' * num_of_hash + ' ' * (n - num_of_hash - percentnum_length) + percentnum
                return string

            output = f"Poll for {name}\nTaken around {date}\n\n"
            for key, result in results.items():
                output += f"{PartyIdtoName[int(key)]} |{fill_hash(35, result)}|\n"

            output = chatformat.mono(output)
            self.reply_text(output)

    @command(pass_args=False, register_help=False, allow_inline=True)
    def rng(self):
        """
        chosen by fair dice roll
        guaranteed to be random
        """
        self.reply_text("4")
