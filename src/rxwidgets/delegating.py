import operator
from copy import copy
from typing import Callable


def delegating(*, decorator: Callable[[Callable], Callable], include_reverse=True):
    """
    Decorate a class to map delegate all functions somehow, wrapping each operator in a decorator.

    Args:
        decorator: Decorator to wrap each function with.
        include_reverse: If False, do not include mocked functions like '__radd__'.

    Returns: A decorator for a class.
    """
    def reversing_arguments(fn: Callable):
        def function(a, b):
            return fn(b, a)
        return function

    def decorate(klass):
        klass = copy(klass)

        operators = set(filter(lambda op: op.startswith('__'), dir(operator)))
        operators -= {'__name__'}

        for fn_name in operators:
            fn = getattr(operator, fn_name)
            setattr(klass, fn_name, decorator(fn))

        if include_reverse:
            # From https://docs.python.org/3/reference/datamodel.html#object.__radd__
            # These are needed for things like b + a to work.
            for fn_name, fn in {
                '__radd__': operator.__add__,
                '__rsub__': operator.__sub__,
                '__rmul__': operator.__mul__,
                '__rmatmul__': operator.__matmul__,
                '__rtruediv__': operator.__truediv__,
                '__rfloordiv__': operator.__floordiv__,
                '__rmod__': operator.__mod__,
                # '__rdivmod__': operator.__divmod__,  # Does not exist
                '__rpow__': operator.__pow__,
                '__rlshift__': operator.__lshift__,
                '__rrshift__': operator.__rshift__,
                '__rand__': operator.__and__,
                '__rxor__': operator.__xor__,
                '__ror__': operator.__or__,
            }.items():
                setattr(klass, fn_name, decorator(reversing_arguments(fn)))

        # Not included in operator.
        setattr(klass, '__getattr__', decorator(getattr))

        def call(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        # Equivalent to operator.call, added in python 3.11
        setattr(klass, '__call__', decorator(call))

        return klass

    return decorate
