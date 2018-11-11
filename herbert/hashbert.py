"""
Herbert Submodule
@see herbert.core

Provides an interface to several
Hashing algorithms
"""
from common.basic_utils import t_arr_to_bytes, tx_assert
from decorators import *

from basebert import BaseBert

import hashlib as hl
import base64 as b64
import re

__all__ = ["HashBert"]


class HashBert(BaseBert):
    @command
    def md5(self, args):
        """
        Return the md5-hash of the given string
        """
        self.send_message(hl.md5(t_arr_to_bytes(args)).hexdigest())

    @aliases('sha512', 'hash', 'sha')
    @command
    def sha512(self, args):
        """
        Return the sha512-hash of the given string
        """
        self.send_message(hl.sha512(t_arr_to_bytes(args)).hexdigest())

    @command
    def b64enc(self, args):
        """
        Base64-encode the given string
        """
        self.send_message(b64e(args))

    @command
    def b64dec(self, args):
        """
        Base64-decode the given string
        """
        self.send_message(b64d(args))

    @command
    def hashit(self, args):
        """
        Run a string through all available hash-functions
        """
        import telegram
        self.send_message(hash_all(t_arr_to_bytes(args)), parse_mode=telegram.ParseMode.MARKDOWN)

    @aliases('rotate', 'shift', 'ceasar')
    @command
    def rot(self, args):
        """
        Shift every letter of the string by <n> positions
        """
        tx_assert(len(args) >= 2, "Not enough arguments: /rot <shift> <text>")

        shift, *rest = args

        res = rotate(int(float(shift)), " ".join(rest))

        self.send_message(res)


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
    return b64.b64encode(t_arr_to_bytes(args)).decode("utf-8")


def b64d(args):
    return b64.b64decode(t_arr_to_bytes(args)).decode("utf-8")
