from decorators import command
from basebert import BaseBert


class PingBert(BaseBert):
    @command(pass_args=False, pass_string=True)
    def ping(self, string):
        """
        Pong.
        """
        self.send_message('pong')
        self.send_message(f'Your string was `"{string}"`')
