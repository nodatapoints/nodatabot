from decorators import *
from basebert import *

import path

from ctypes import create_string_buffer as buf, cdll


__all__ = ['InterpRert', 'h_bf']

path.change_path()

# TODO make other architectures available
try:
    h_bf = cdll.LoadLibrary('ext/brainfuck/libbf_x86_64-linux-gnu.so')
except Exception:
    print("Warning: cdll could not find libbf.so. Did you `make`?")
    raise


class InterpRert(BaseBert):
    @aliases('bf')
    @command(pass_args=False, pass_string=True, allow_inline=True)
    def brainfuck(self, string):
        """
        Interpret the message as brainfuck-code
        """
        self.reply_str(run_bf(bytes(string, encoding="utf-8")) or "(No decodable output)", parse_mode=None)


def has_invalid_bytes(byte_str):
    for bt in byte_str:
        if (bt <= 31 or bt >= 127) and bt != 10:
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

