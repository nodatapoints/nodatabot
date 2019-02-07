import datetime
from decorators import command
from basebert import InlineBaseBert


class PingBert(InlineBaseBert):
    @command(pass_args=False)
    def ping(self):
        """
        Pong.
        """
        self.send_message('pong')

    @command(pass_string=True, allow_inline=True)
    def echo(self, string):
        """
        Whatever you say.
        """
        self.reply_text(string)

    @command(pass_args=False, register_help=False)
    def pong(self):
        """
        Easter Egg
        """
        self.send_message('So you think you\'re clever, huh?')

    @command(pass_args=False)
    def time(self):
        """prints the current time and date"""
        self.send_message(str(datetime.datetime.now()))
