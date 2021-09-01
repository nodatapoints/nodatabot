"""
Sometimes, you have some classes representing state,
and you really want to do some operations that need
to be grouped together, so spreading it over
instance methods of all subclasses is really not
nice.

In that case, you can do something way more
hacky, and essentially do a 2d table dispatch
over all subclasses.

This module makes doing this way easier, and
avoids spamming accept() functions everywhere
in the data classes.
"""
from inspect import getargs
from typing import Callable, Any, Dict


class HandlerError(Exception):
    """
    Complain in case a handler definition is
    invalid, e.g. in case someone tries
    to register a function for a certain
    type twice with the same dispatch
    """


def _raise_err(_self, key, instances):
    raise Exception(f"No handler installed for {key}.")


class TypeDispatchProcessor:
    """
    Use instances of this class as a decorator
    to register functions, then call .invoke()
    to automatically dispatch some arguments
    to the correct registered function.

    Example: there are subclasses of `Data`
    that carry some important data, and
    you want to do something for each concrete
    subtype.

    class DataProcessor:
        _handle = TypeDispatchProcessor(Data)

        @_handle.process
        def handle_d1(data: ConcreteData1):
            ...

        @_handle.process
        def handle_d2(data: ConcreteData2):
            ...

        def __call__(self, any_data: Data):
            return DataProcessor._handle.invoke(any_data)

    Of course, this dispatch can equivalently be
    performed using a series of isinstance checks.
    However, this becomes more difficult once
    there are several arguments which need to
    be dispatched, leading to a nested lookup.

    The other way to implement this would be
    a polymorphic double dispatch, (visitor pattern),
    where each data member needs to implement an
    accept method that calls the correct method
    of the calling behaviour passing itself.

    That requires too many seemingly useless,
    detached-from-everything functions for my taste,
    though, so we do this dispatch using a bunch
    of decorators.

    This might not be a good way to do anything,
    by the way, but it __does__ save some typing.
    """
    def __init__(self, *classes, invalid_call=_raise_err):
        self._dispatch_table = dict()
        self._classes = (classes,) if isinstance(classes, type) else tuple(classes)
        self.invalid_call = invalid_call
        self._width = len(self._classes)

    def process(self, function: Callable[..., Any], with_self=False) -> None:
        """
        Add a function to the dispatch handlers, using the types defined
        in the annotations of the arguments
        Automatically delegates to self.generate if the passed object
        is a class
        """
        args = tuple(getargs(function.__code__).args)

        if with_self:
            args = args[1:]

        for arg in args:
            if arg not in function.__annotations__:
                raise HandlerError(f'Argument {arg} not annotated in handler {function}.')

        subclasses = tuple(function.__annotations__[arg] for arg in args)
        assert len(subclasses) == self._width

        key = subclasses
        if key in self._dispatch_table:
            raise HandlerError(
                f"A call via {key} is already handled by {self._dispatch_table[key]}.")

        self._dispatch_table[key] = lambda *a: function(self, *a) if with_self else function

    def invoke(self, *instances):
        """
        Do the actual dispatch using an instance of a
        subclass of each type
        """
        assert len(instances) == self._width
        key = tuple(i.__class__ for i in instances)
        if key not in self._dispatch_table:
            return self.invalid_call(self, key, instances)
        return self._dispatch_table[key](*instances)


class TypeDispatch(type):
    """
    Metaclass to register all non-private member methods of
    a class as valid dispatch targets

    Equivalent to adding a process-decorator before each
    method not starting with an underscore

    Set the array of types to dispatch over as a _types
    class member

    This will make the processor available as a _processor
    class member, and bind the invoke operation to the call
    operator of instances of the class
    """
    def __new__(cls, cls_name: str, bases: tuple, namespace: Dict[str, Callable[..., Any]]):
        type_member = '_types'
        try:
            processor = TypeDispatchProcessor(*namespace[type_member])
        except KeyError as err:
            raise ValueError(f'Expected class with \'{type_member}\' member') from err

        res: Dict[str, Callable[..., Any]] = dict()
        for name, member in namespace.items():
            if len(name) == 0 or name[0] == '_':
                continue

            assert not isinstance(member, type), 'No recursion allowed'
            processor.process(member, with_self=True)

        if (handler := namespace.get('_dispatch_fail', None)):
            processor.invalid_call = handler

        res['__call__'] = lambda self, *args: processor.invoke(*args)
        res['__init__'] = lambda self: None
        res['_processor'] = processor

        return type.__new__(cls, cls_name, bases, res)
