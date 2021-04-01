"""
Provides error classes.

Raising Exceptions of these types will
cause them to be reported to the user.
All other exceptions will be logged, and
only a generic failure message will be sent.

These error types should be subclassed where
appropriate.

Herberror is meant for general problems like
invalid arguments or invalid api responses,
BadHerberror is meant for cases where a
contract is violated and a function has
unexpected internal state problems
"""


class Herberror(Exception):
    """Basic Herbert error"""


class BadHerberror(Herberror):
    """Something someone needs to actually go and fix"""
