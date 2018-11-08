from decorators import command
from basebert import BaseBert


class PingBert(BaseBert):
    @command(pass_args=False)
    def ping(self):
        """
        Pong.
        """
        self.send_message('pong')

    @command(pass_args=False, pass_string=True)
    def echo(self, string):
        """
        Whatever you say.
        """
        self.send_message(string)
