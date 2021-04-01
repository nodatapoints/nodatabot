"""
Provides decorators that do not depend on any
telegram bot methods or classes
"""
from typing import Callable
from functools import partial


def argdecorator(func):
    """
    decorator decorating a decorator, to convert it to a decorator-generating function.
    """

    def argreceiver(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return func(*args, **kwargs)
        return lambda method: func(method, *args, **kwargs)

    return argreceiver


@argdecorator
def as_partial(_: Callable, base: Callable, *args, **kwargs):
    """
    Allows defining a function as the invocation of another function
    with some parameters already bound to values

    i.e.

    @as_partial(other_function, arg1)
    def do_something(arg):
        pass

    will lead to calls
    do_something(hello) -> other_function(arg1, hello)
    """
    return partial(base, *args, **kwargs)
