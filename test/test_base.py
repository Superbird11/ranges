"""
Testing helper functions
"""
from pytest import fail


def asserterror(errortype, func, args=None, kwargs=None):
    """
    A helper method - basically, "execute the given function with the given args and
    assert that it produces the correct error type.
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    try:
        func(*args, **kwargs)
        fail(f"Function {func.__name__} with args {args} and kwargs {kwargs} should have raised {errortype.__name__}")
    except errortype:
        pass