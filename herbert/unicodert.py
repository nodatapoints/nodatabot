import re

from basebert import Herberror, InlineBaseBert
from common.constants import FLAG_CHARS
from decorators import command, aliases

__all__ = ['UniCoDert']


def _translate_char(c: chr):
    assert 'A' <= c <= 'Z'
    return FLAG_CHARS[ord(c) - ord('A')]


class UniCoDert(InlineBaseBert):

    @aliases('flag', 'flg')
    @command(pass_string=True, allow_inline=True)
    def makeflag(self, string: str):
        """
        Make unicode flags from country names

        Takes a string of capital letters (no spaces!) \
        and returns the corresponding unicode characters \
        representing the country codes flag.

        Try /flg US or /flg DE or /flg JP etc
        """
        string = string.strip()
        if re.match(r'^[A-Z]+$', string) is None:
            raise Herberror("Argument must be a Sequence of CAPITAL LETTERS")

        res = ''
        for c in string:
            res += _translate_char(c)

        self.reply_text(res)
