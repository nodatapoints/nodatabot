from decorators import *
from basebert import *

import path

from ctypes import create_string_buffer as buf, cdll

__all__ = ['InterpRert', 'h_bf']

from common.chatformat import mono

MAX_INSTRUCTIONS = 1000000
OUT_SIZE = 512

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

        Interpret the given string as brainfuck. Brainfuck is a minimalistic, esoteric, but turing-complete \
        programming language operating on a linear storage tape with exactly 8 instructions:
        {mono('+')} - increment the value in the current tape slot
        {mono('-')} - decrement the value
        {mono('>')} - move to the next tape slot
        {mono('<')} - move to the previous tape slot
        {mono('[')} - begin a loop block
        {mono(']')} - if the current value is not 0, jump to the corresponding {mono('[')}. end a loop block.
        {mono('.')} - print the value in the current slot as a byte
        {mono(',')} - read a value - not implemented in this version

        Limits:
        To avoid overly long calculation times and/or memory usage, this interpreter limits the number of executed \
        instructions to {MAX_INSTRUCTIONS}, the number of output bytes to {OUT_SIZE} and the tape length to 512. \
        Input Program size is theoretically unlimited, but has to fit in a single telegram message, which is, again, \
        of constrained size.
        """
        self.reply_text(run_bf(bytes(string, encoding="utf-8")) or "(No decodable output)", parse_mode=None)


def has_invalid_bytes(byte_str):
    for bt in byte_str:
        if (bt <= 31 or bt >= 127) and bt != 10:
            return True

    return False


def run_bf(prog):
    b = buf(OUT_SIZE)
    result = h_bf.execute(prog, b, OUT_SIZE, MAX_INSTRUCTIONS)

    if result is 1:
        raise Herberror("Wow, that _timed out_. Good job...")
    elif result is 3:
        raise Herberror("Well, this is certainly not even valid in brainfuck.")
    else:
        if has_invalid_bytes(b.value):
            return str(b.value)
        else:
            return b.value.decode("utf-8")
