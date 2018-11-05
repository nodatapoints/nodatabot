from decorators import command
from basebert import BaseBert


class PingBert(BaseBert):
    @command(pass_args=False)
    def ping(self):
        self.send_message('pong')
