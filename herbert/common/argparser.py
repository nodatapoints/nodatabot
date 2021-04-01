"""
Provide very basic key-value argument parsing
for arbitrary strings
"""
from typing import SupportsInt, SupportsFloat, Callable, Tuple, List, Dict, Union
import re

from herberror import Herberror

from common.basic_utils import nth
from common.constants import SEP_LINE

__all__ = ['Args', 'ArgParser', 'dict_map']


class UnexpectedArgument(Herberror):
    """ Something wasn't quite right """


class ArgumentFormatError(Herberror):
    """ e.g. missing brackets in arg string """


def _check_if_int(maybe_int: Union[str, bytes, SupportsInt]) -> Tuple[bool, int]:
    try:
        return True, int(maybe_int)
    except ValueError:
        return False, 0


def _check_if_float(maybe_float: Union[str, bytes, SupportsFloat]) -> Tuple[bool, float]:
    try:
        return True, float(maybe_float)
    except ValueError:
        return False, 0.


def _check_if_chars_in(string, charset):
    for c in string:
        if c not in charset:
            return False, ""

    return True, string


def dict_map(table: dict):
    """ convert a dict to a lookup function """
    def map_fn(key):
        return table[key]

    return map_fn


class ArgParser:
    """
    Each instance of this class should be able to
    - check if it can understand an argument
    - return the parsed value of an argument

    A series of such ArgParser objects is used to convert an entire argument string
    """
    def __init__(self, check: Callable = None, value: Callable = None, accept: Callable = None, explain: str = ""):
        self.explain = explain + "\n"
        if accept is not None:
            assert check is None, "Invalid ArgParser Construction"
            assert value is None, "Invalid ArgParser Construction"
            self.check = lambda x: accept(x)[0]
            self.value = lambda x: accept(x)[1]
        else:
            assert check is not None, "Invalid ArgParser Construction"
            assert value is not None, "Invalid ArgParser Construction"
            self.check = check
            self.value = value

    def map(self, map_fn: Callable):
        """ function for converting the output values of a given parser """
        return ArgParser(self.check, lambda s: map_fn(self.value(s)))

    def and_require(self, secondary_check_fn: Callable, explain: str = None):
        """ function to extend the constraints on the input values """
        explain = explain or ""
        return ArgParser(lambda s: self.check(s) and secondary_check_fn(s), self.value, explain=self.explain + explain)

    def bounded(self, min_val: object = 0, max_val: object = 1, limits: Tuple[object, object] = (0, 1)):
        """ extends the constraints by requiring the value to lie in a certain interval """
        return self.and_require(lambda s: min_val or limits[0] <= self.value(s) <= max_val or limits[1],
                                explain=f"Value has to be in Range [{limits[0]}..{limits[1]}].")


class Args:
    """
    Wrapper namespace for interface argument parsing methods
    """
    @staticmethod
    def parse(string: str, expected_arguments: Dict[str, ArgParser], begin="[", end="]") -> Tuple[dict, str]:
        """ Parse [key=value, k=v] arg pairs at start of string and return rest """
        # the string needs to start with "[" (+- some whitespace)
        # and contain comma-separated key=value pairs until the closing "]"
        string = string.strip()

        if len(string) == 0 or string[0] != begin:
            return dict(), string

        res = dict()

        parts = re.split(end, string[len(begin):], maxsplit=1)
        kv_pairs = re.split(',', parts[0])

        for kv_pair in kv_pairs:
            try:
                key, raw_value = re.split('=', kv_pair, maxsplit=1)
            except ValueError as err:
                raise ArgumentFormatError(f'Invalid Argument Format: No value for key in \'{kv_pair}\'') from err

            key = key.strip()
            raw_value = raw_value.strip()

            if key not in expected_arguments:
                raise UnexpectedArgument(f'Got unexpected argument \'{key}\' with value \'{raw_value}\'')

            if not expected_arguments[key].check(raw_value):
                raise ArgumentFormatError(f'Invalid argument value \'{raw_value}\' for key \'{key}\'' +
                                          (f'\n{SEP_LINE}\n{expected_arguments[key].explain}'
                                           if expected_arguments[key].explain else ''))

            res[key] = expected_arguments[key].value(raw_value)

        return res, parts[1]

    @staticmethod
    def parse_positional(string: str, expected_arguments: List[ArgParser]):
        """ apply argparsers sequentially from an ordered list """
        string = string.strip()
        argc = len(expected_arguments)
        parts = re.split(r",?\s+", string)

        if len(parts) < argc:
            raise Herberror(f"Too few arguments! ({argc} expected)")

        if len(parts) > argc:
            raise Herberror(f"Too many arguments! ({argc} expected)")

        res = []
        for i, part in enumerate(parts):
            exp_arg = expected_arguments[i]
            if not exp_arg.check(part):
                raise ArgumentFormatError(f"Invalid Argument Type for {nth(i+1)} arg (given \'{part}\')" +
                                          (f"\n{SEP_LINE}\n{exp_arg.explain}" if exp_arg.explain else ''))
            res.append(exp_arg.value(part))

        return res

    class ArgumentType:
        """
        Wrapper namespace class for several useful basic ArgParsers
        """
        BOOL = ArgParser(
            check=lambda s: re.match('^([Tt]rue?|[Ff]alse?|1|0|y(es)?|no?)$', s) is not None,
            value=lambda s: re.match('^([Tt]rue?|1|y(es)?)$', s) is not None,
            explain="Expecting a Boolean Value (matching ^([Tt]rue?|[Ff]alse?|1|0|y(es)?|no?)$)"
        )

        INT = ArgParser(accept=_check_if_int, explain="Expecting an Integer Value")
        FLOAT = ArgParser(accept=_check_if_float, explain="Expecting a Floating Point Numeric Value")

        STR = ArgParser(
            check=lambda s: True,
            value=lambda s: s,
            explain="Expecting a String Value"
        )

        @staticmethod
        def one_of(*args):
            """ matches if the parsed value is one of the given arguments """
            return ArgParser(
                check=lambda s: s in args,
                value=lambda s: s,
                explain=f"Expecting Value to be one of {args}."
            )

        @staticmethod
        def char_in(string: str):
            """ matches if the parsed value is a single character contained in string """
            return ArgParser(
                check=lambda s: len(s) == 1 and s in string,
                value=lambda s: s,
                explain=f"Expecting Value to be a single character in [{string}]"
            )

        @staticmethod
        def chars_in(string: str):
            """ matches if the parsed value is a string composed of characters contained in string """
            return ArgParser(
                accept=lambda s: _check_if_chars_in(s, string),
                explain=f"Expecting Value to be a String consisting of characters in [{string}]"
            )

        @staticmethod
        def from_dict(dct: dict):
            """ matches if the parsed value is a key in dct, returns the corresponding value """
            return Args.T.one_of(*dct.keys()).map(dict_map(dct))

        @staticmethod
        def matching(regexp: str):
            """ matches if the given regexp matches """
            return ArgParser(
                lambda s: re.match(regexp, s) is not None,
                lambda s: re.match(regexp, s),
                explain=f'Expected Value to match {regexp}'
            )

    T = ArgumentType
