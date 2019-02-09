import re

from basebert import Herberror, InlineBaseBert
from decorators import command, aliases

__all__ = ['UniCoDert']


FLAG_CHARS = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"


def _translate_char(c: chr):
    assert 'A' <= c <= 'Z'
    return FLAG_CHARS[ord(c) - ord('A')]


class UniCoDert(InlineBaseBert):

    @aliases('flag', 'flg')
    @command(pass_string=True)
    def makeflag(self, string: str):
        string = string.strip()
        if re.match(r'^[A-Z]+$', string) is None:
            raise Herberror("Argument must be a Sequence of CAPITAL LETTERS")

        res = ''
        for c in string:
            res += _translate_char(c)

        self.reply_text(res)
