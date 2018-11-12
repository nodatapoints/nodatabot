from core import *
from basebert import BaseBert
from decorators import *


class TestBert(BaseBert):
    @command(pass_string=True)
    def fakeinline(self, string):
        handle_inline_query(self.bot, self.update, line=string)

    @command(pass_args=False)
    def testinline(self, inline_query=None, inline_args=[]):
        self.send_message("no or faking" if inline_query is None else "inline")
        self.send_message("Got args: " + " ".join(inline_args))
