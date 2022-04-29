from dataclasses import dataclass
from typing import Any, Callable

from rxwidgets.decorators import optional_arg_decorator


@dataclass
class ValueBox:
    """
    A simple wrapper for either objects or Exceptions. Call .unbox() to find out which!
    """
    value: Any
    is_error: bool = False

    def unbox(self):
        if self.is_error:
            raise self.value from None
        return self.value


def unbox_parameters(args, kwargs, *, strict=True):
    """
    Unbox args and kwargs.

    Args:
        strict: If true, raise if any argument is not a `ValueBox`.
            If False, treat as if they were `ValueBox(value)`.

    Returns: args, kwargs
    """
    def convert(arg):
        if not isinstance(arg, ValueBox):
            if strict:
                raise ValueError(f"Not a ValueBox: {arg}")
            return arg

        return arg.unbox()

    args_unboxed = [convert(arg) for arg in args]
    kwargs_unboxed = {key: convert(arg) for key, arg in kwargs.items()}

    return args_unboxed, kwargs_unboxed


@optional_arg_decorator
def function(fun, *, strict=True) -> Callable[..., ValueBox]:
    def fun_boxed(*args, **kwargs):
        try:
            args_unboxed, kwargs_unboxed = unbox_parameters(args, kwargs, strict=strict)

            result = fun(*args_unboxed, **kwargs_unboxed)

            return ValueBox(result)
        except Exception as e:
            return ValueBox(e, is_error=True)
    return fun_boxed
