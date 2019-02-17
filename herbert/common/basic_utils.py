"""
Here go utility functions, which cannot
be classified AND have no dependencies
on libraries or other code not in this
exact module.
"""
from common.constants import NUM_SUFFIXES


def arr_to_bytes(arr):
    """
    "Converts" an array to a sequence of bytes by joining
    using byte 10d and then applying the unicode-encoding
    """
    return str_to_bytes(" ".join([str(x) for x in arr]))


def str_to_bytes(string):
    """
    Convert a string to its python-byte representation using
    the utf-8 character encoding
    """
    return bytes(string, encoding="utf-8")


def nth(num: int):
    if num >= len(NUM_SUFFIXES):
        idx = 0
    else:
        idx = num
    return f"{num}{NUM_SUFFIXES[idx]}"
