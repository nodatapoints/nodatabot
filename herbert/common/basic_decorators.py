from typing import Callable


def argdecorator(fn):
    """
    decorator decorating a decorator, to convert it to a decorator-generating function.
    """
    def argreceiver(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(*args, **kwargs)
        return lambda method: fn(method, *args, **kwargs)

    return argreceiver


@argdecorator
def as_partial(_: Callable, base: Callable, *args, **kwargs):
    from functools import partial
    return partial(base, *args, **kwargs)