from decorators import command
from basebert import BaseBert


class PingBert(BaseBert):
    def __init__(self):
        super().__init__()

    @command(pass_args=False)
    def ping(self):
        self.send_message('pong')
