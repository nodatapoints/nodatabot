"""
Here go utility functions, which cannot
be classified AND have no dependencies
on libraries or other code not in this
exact module.
"""


def arr_to_bytes(arr: list):
    """
    "Converts" an array to a sequence of bytes by joining
    using byte 10d and then applying the unicode-encoding
    """
    return str_to_bytes(" ".join([str(x) for x in arr]))


def str_to_bytes(string: str) -> bytes:
    """
    Convert a string to its python-byte representation using
    the utf-8 character encoding
    """
    return bytes(string, encoding="utf-8")


def bytes_to_str(bytestr: bytes) -> str:
    """
    Try to convert a byte sequence to a decoded
    character sequence
    """
    try:
        return bytestr.decode("utf-8")
    except UnicodeDecodeError:
        return str(bytestr)


def require(_arg):
    """ Mark some value as used """


def nth(num: int) -> str:
    """ return a string representing the ordinal of num (1st, 2nd, 3rd, ...) """
    num_suffixes = ['th', 'st', 'nd', 'rd']
    if num >= len(num_suffixes):
        idx = 0
    else:
        idx = num
    return f"{num}{num_suffixes[idx]}"


def utf16len(string: str) -> int:
    """
    Return the number of utf16 codepoints in the string
    """
    return len(string.encode("utf-16le")) // 2
