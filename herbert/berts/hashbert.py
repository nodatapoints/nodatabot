"""
Herbert Submodule
@see herbert.core

Provides an interface to several
Hashing algorithms
"""
import hashlib as hl
import base64 as b64
import re

from common.basic_utils import str_to_bytes, bytes_to_str
from common.herbert_utils import tx_assert
from common.constants import ONLY_BASIC_HELP
from common.chatformat import STYLE_MD
from decorators import command, doc, aliases

from basebert import BaseBert
from herberror import Herberror

__all__ = ["HashBert"]


class HashBert(BaseBert):
    """
    Wraps several hashing commands, and
    a letter shift obfuscator
    """

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
        self.send_message(hash_all(str_to_bytes(string)),
                          parse_mode=STYLE_MD)

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
        except ValueError as err:
            raise Herberror(f'shift \'{shift}\' is not a valid integer') from err

        self.reply_text(res, parse_mode=None)


def rotate_char(shift, char, low, high):
    return chr((shift + ord(char) - ord(low)) % (ord(high) - ord(low) + 1) + ord(low))


def rotate(shift, string):
    """
    Obfuscate a string by rotating all alphabetic characters
    by some shift value (e.g. shift=1 takes A to B, E to F, etc)
    """
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
    """
    Run all available hash functions
    """
    res = ""
    for name in hl.algorithms_available:
        try:
            hash_state = hl.new(name)
            hash_state.update(arg)
            res += f"{re.sub('_', '-', name)}: ```{hash_state.hexdigest()}```\n\n"
        except TypeError:
            pass

    return res


def b64e(args):
    """
    Base64 encode
    """
    try:
        return bytes_to_str(b64.b64encode(str_to_bytes(args)))
    except b64.binascii.Error as err:
        raise Herberror(f"Couldn't decode: {err}") from err


def b64d(args):
    """
    Base64 decode
    """
    try:
        return bytes_to_str(b64.b64decode(str_to_bytes(args)))
    except b64.binascii.Error as err:
        raise Herberror(f"Couldn't decode: {err}") from err
