from decorators import *
from basebert import *

import multiprocessing
import time

from ctypes import create_string_buffer as buf, cdll


# TODO make other architectures available
h_bf = cdll.LoadLibrary('ext/brainfuck/libbf_x86_64-linux-gnu.so')


class InterpRert(BaseBert):
    @aliases('bf')
    @command(pass_args=False, pass_string=True)
    def brainfuck(self, string):
        """
        Interpret the message as brainfuck-code
        """
        self.send_message(run_bf(bytes(string, encoding="utf-8")) or "(No decodable output)", parse_mode=None)


def run_bf(prog):
    b = buf(512)

    result = h_bf.execute(prog, b, 1000000)

    if result is 1:
        raise Herberror("Wow, that _timed out_. Good job...")
    elif result is 3:
        raise Herberror("Well, this is certainly not even valid in brainfuck.")
    else:
        try:
            return b.value.decode("utf-8")
        except UnicodeError:
            return str(b.value)

