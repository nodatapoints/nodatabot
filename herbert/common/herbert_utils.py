"""
Utils for basebert and core
"""
from basebert import Herberror
import inspect


def tx_assert(condition, msg, err_class=Herberror):
    """ throw the given error if the condition evaluates to False """
    if not condition:
        raise err_class(msg)


def getmethods(cls):
    """ return a list of all member methods of cls """
    return inspect.getmembers(cls, inspect.ismethod)


def is_own_method(method, cls):
    """ return whether m is actually member of cls or just inherited """
    for baseclass in cls.__class__.__bases__:
        if hasattr(baseclass, method.__name__):
            return False
    return True


def is_cmd_decorated(method):
    """ return whether or not fn has the cmdinfo member """
    return hasattr(method, 'cmdinfo')
