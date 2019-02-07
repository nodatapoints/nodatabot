"""
Herbert Submodule
@see herbert.core

Provides an interface to several
Hashing algorithms
"""
from common.basic_utils import str_to_bytes
from common.herbert_utils import tx_assert
from decorators import *

from basebert import InlineBaseBert

import hashlib as hl
import base64 as b64
import re

__all__ = ["HashBert"]


class HashBert(InlineBaseBert):
    @command(pass_string=True, allow_inline=True)
    def md5(self, string):
        """
        Return the md5-hash of the given string
        """
        self.reply_text(hl.md5(str_to_bytes(string)).hexdigest())

    @aliases('sha512', 'hash', 'sha')
    @command(pass_string=True, allow_inline=True)
    def sha512(self, string):
        """
        Return the sha512-hash of the given string
        """
        self.reply_text(hl.sha512(str_to_bytes(string)).hexdigest())

    @command(pass_string=True, allow_inline=True)
    def b64enc(self, string):
        """
        Base64-encode the given string
        """
        self.reply_text(b64e(string))

    @command(pass_string=True, allow_inline=True)
    def b64dec(self, string):
        """
        Base64-decode the given string
        """
        self.reply_text(b64d(string))

    @command(pass_string=True)
    def hashit(self, string):
        """
        Run a string through all available hash-functions
        """
        import telegram
        self.send_message(hash_all(str_to_bytes(string)), parse_mode=telegram.ParseMode.MARKDOWN)

    @aliases('rotate', 'shift', 'ceasar')
    @command(allow_inline=True)
    def rot(self, args):
        """
        Shift every letter of the string by n positions

        ebg 13 vf avpr orpnhfr rapbqvat naq qrpbqvat vf gur fnzr bssfrg
        """
        tx_assert(len(args) >= 2, "Not enough arguments: /rot <shift> <text>")

        shift, *rest = args

        res = rotate(int(float(shift)), " ".join(rest))

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
    return b64.b64encode(str_to_bytes(args)).decode("utf-8")


def b64d(args):
    return b64.b64decode(str_to_bytes(args)).decode("utf-8")
