from basebert import Herberror


def tx_assert(condition, msg, err_class=Herberror):
    if not condition:
        raise err_class(msg)
