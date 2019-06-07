import re

from basebert import Herberror, InlineBaseBert
from common.constants import FLAG_CHARS
from decorators import command, aliases, doc

__all__ = ['UniCoDert']


def _translate_char(c: str):
    assert len(c) == 1 and 'A' <= c <= 'Z'
    return FLAG_CHARS[ord(c) - ord('A')]

def _retranslate_char(c: str):
    assert len(c) == 1 and c in FLAG_CHARS
    return chr(ord('A') + FLAG_CHARS.find(c))


class UniCoDert(InlineBaseBert):

    @aliases('flag', 'flg')
    @command(pass_string=True, allow_inline=True)
    @doc(
        """
        Make unicode flags from country names

        Takes a string of capital letters (no spaces!) \
        and returns the corresponding unicode characters \
        representing the country codes flag.

        e.g: m§/flg US§, m§/flg DE§, m§/flg JP§ etc.
        """
    )
    def makeflag(self, string: str):
        string = string.strip()
        if re.match(r'^[A-Z]+$', string) is None:
            raise Herberror("Argument must be a Sequence of CAPITAL LETTERS")

        res = ''
        for c in string:
            res += _translate_char(c)

        self.reply_text(res)

    @command(pass_string=True, register_help=False)
    def reverseflg(self, string: str):
        string = string.strip()
        res = ''
        try:
            for c in string:
                res += _retranslate_char(c)
        except AssertionError:
            raise Herberror("Well, that sucks. That is, you do.")

        self.reply_text(res)
