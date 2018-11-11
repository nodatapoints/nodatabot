from decorators import *
from basebert import *

from ctypes import create_string_buffer as buf, cdll


__all__ = ['InterpRert', 'h_bf']


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


def has_invalid_bytes(bytestr):
    for bt in bytestr:
        if bt <= 31 or bt >= 127:
            return True

    return False


OUT_SIZE = 512


def run_bf(prog):
    b = buf(OUT_SIZE)
    result = h_bf.execute(prog, b, OUT_SIZE, 1000000)

    if result is 1:
        raise Herberror("Wow, that _timed out_. Good job...")
    elif result is 3:
        raise Herberror("Well, this is certainly not even valid in brainfuck.")
    else:
        if has_invalid_bytes(b.value):
            return str(b.value)
        else:
            return b.value.decode("utf-8")

