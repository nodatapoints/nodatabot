from basebert import Herberror
import inspect


def tx_assert(condition, msg, err_class=Herberror):
    if not condition:
        raise err_class(msg)


def getmethods(cls):
    return inspect.getmembers(cls, inspect.ismethod) 


def is_own_method(m, cls):
    for baseclass in cls.__class__.__bases__:
        if hasattr(baseclass, m.__name__):
            return False
    return True


def is_cmd_decorated(fn):
    return hasattr(fn, 'cmdinfo')
