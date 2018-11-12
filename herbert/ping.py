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
        self.reply_str(string)

    @command(pass_args=False, register_help=False)
    def pong(self):
        """
        Easter Egg
        """
        self.send_message('So you think you\'re clever, huh?')
