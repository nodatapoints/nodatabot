"""
Bert

enables checking the avaliability of this herbert instance

provides commands:
    - ping
    - echo
"""
import datetime
from decorators import command, doc
from basebert import BaseBert


class PingBert(BaseBert):
    """ bert - allow pinging """

    @command(pass_args=False)
    @doc(""" Pong. """)
    def ping(self):
        self.send_message('pong')

    @command(pass_string=True, allow_inline=True)
    @doc(""" Whatever you say. """)
    def echo(self, string):
        self.reply_text(string)

    @command(pass_args=False, register_help=False)
    @doc(""" Easter Egg """)
    def pong(self):
        self.send_message('So you think you\'re clever, huh?')

    @command(pass_args=False)
    @doc(""" prints the current time and date """)
    def time(self):
        self.send_message(str(datetime.datetime.now()))
