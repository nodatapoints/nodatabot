from basebert import Herberror
import re

__all__ = ['Args']


class UnexpectedArgument(Herberror):
    """ Something wasn't quite right """


class ArgumentFormatError(Herberror):
    """ e.g. missing brackets in arg string """


def _check_if_int(s):
    try:
        return True, int(s)
    except ValueError:
        return False, 0


def _check_if_float(s):
    try:
        return True, float(s)
    except ValueError:
        return False, 0.


class ArgParser:
    def __init__(self, check=None, value=None, accept=None):
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


class Args:
    @staticmethod
    def parse(string: str, expected_arguments: dict):
        """ Parse [key=value, k=v] arg pairs at start of string and return rest """
        # the string needs to start with "[" (+- some whitespace)
        # and contain comma-separated key=value pairs until the closing "]"
        string = string.strip()

        if len(string) == 0 or string[0] != "[":
            return None, string

        res = dict()

        parts = re.split(r"\]", string[1:], maxsplit=1)
        kv_pairs = re.split(',', parts[0])

        for kv_pair in kv_pairs:
            try:
                key, raw_value = re.split('=', kv_pair, maxsplit=1)
            except ValueError:
                raise ArgumentFormatError(f'Invalid Argument Format: No value for key in \'{kv_pair}\'')

            key = key.strip()
            raw_value = raw_value.strip()

            if key not in expected_arguments:
                raise UnexpectedArgument(f'Got unexpected argument \'{key}\' with value \'{raw_value}\'')

            if not expected_arguments[key].check(raw_value):
                raise ArgumentFormatError(f'Invalid argument value \'{raw_value}\' for key \'{key}\'')

            res[key] = expected_arguments[key].value(raw_value)

        return res, parts[1]

    class T:
        BOOL = ArgParser(
            check=lambda s: re.match('^([Tt]rue?|[Ff]alse?|1|0|y(es)?|no?)$', s) is not None,
            value=lambda s: re.match('^([Tt]rue?|1|y(es)?)$', s) is not None
        )

        INT = ArgParser(accept=_check_if_int)
        FLOAT = ArgParser(accept=_check_if_float)

        @staticmethod
        def one_of(*args):
            return ArgParser(
                check=lambda s: s in args,
                value=lambda s: s
            )

        @staticmethod
        def bounded(pre_parser: ArgParser, limits: tuple):
            return ArgParser(
                check=lambda s: pre_parser.check(s) and limits[0] <= pre_parser.value(s) <= limits[1],
                value=pre_parser.value
            )
