from basebert import Herberror


def t_arr_to_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")


def tx_assert(condition, msg, err_class=Herberror):
    if not condition:
        raise err_class(msg)