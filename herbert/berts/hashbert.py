"""
Herbert Submodule
@see herbert.core

Provides an interface to several
Hashing algorithms
"""
from common.basic_utils import str_to_bytes, bytes_to_str
from common.herbert_utils import tx_assert
from common.constants import ONLY_BASIC_HELP
from decorators import *

from basebert import InlineBaseBert
from herberror import Herberror

import hashlib as hl
import base64 as b64
import re

__all__ = ["HashBert"]


class HashBert(InlineBaseBert):
    @command(pass_string=True, allow_inline=True, register_help=ONLY_BASIC_HELP)
    @doc(""" Return the md5-hash of the given string """)
    def md5(self, string):
        self.reply_text(hl.md5(str_to_bytes(string)).hexdigest())

    @aliases('sha512', 'hash', 'sha')
    @command(pass_string=True, allow_inline=True)
    @doc(""" Return the sha512-hash of the given string """)
    def sha512(self, string):
        self.reply_text(hl.sha512(str_to_bytes(string)).hexdigest())

    @command(pass_string=True, allow_inline=True)
    @doc(""" Base64-encode the given string """)
    def b64enc(self, string):
        self.reply_text(b64e(string))

    @command(pass_string=True, allow_inline=True)
    @doc(""" Base64-decode the given string """)
    def b64dec(self, string):
        self.reply_text(b64d(string))

    @command(pass_string=True)
    @doc(""" Run a string through all available hash-functions """)
    def hashit(self, string):
        import telegram
        self.send_message(hash_all(str_to_bytes(string)), parse_mode=telegram.ParseMode.MARKDOWN)

    @aliases('rotate', 'shift', 'ceasar')
    @command(allow_inline=True)
    @doc("""
        Shift every letter of the string by n positions

        ebg 13 vf avpr orpnhfr rapbqvat naq qrpbqvat hfrf gur fnzr bssfrg
        """)
    def rot(self, args):
        tx_assert(len(args) >= 2, "Not enough arguments: /rot <shift> <text>")

        shift, *rest = args

        try:
            res = rotate(int(float(shift)), " ".join(rest))
        except ValueError:
            raise Herberror(f'shift \'{shift}\' is not a valid integer')

        self.reply_text(res, parse_mode=None)


def rotate_char(shift, char, low, high):
    return chr((shift + ord(char) - ord(low)) % (ord(high) - ord(low) + 1) + ord(low))


def rotate(shift, string):
    res = ""
    for char in string:
        if 'a' <= char <= 'z':
            res += rotate_char(shift, char, 'a', 'z')
        elif 'A' <= char <= 'Z':
            res += rotate_char(shift, char, 'A', 'Z')
        else:
            res += char
    return res


def hash_all(arg):
    res = ""
    for name in hl.algorithms_available:
        try:
            h = hl.new(name)
            h.update(arg)
            res += f"{re.sub('_', '-', name)}: ```{h.hexdigest()}```\n\n"
        except TypeError:
            pass

    return res


def b64e(args):
    return bytes_to_str(b64.b64encode(str_to_bytes(args)))


def b64d(args):
    return bytes_to_str(b64.b64decode(str_to_bytes(args)))
