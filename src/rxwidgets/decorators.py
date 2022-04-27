import functools


def optional_arg_decorator(decorator):
    @functools.wraps(decorator)
    def wrapped_decorator(fn=None, **kwargs):
        if fn is not None:
            # @decorator or decorator(fn, **kwargs)
            return decorator(fn, **kwargs)

        # @decorator(**kwargs) or decorator(**kwargs)

        def curried_decorator(fn):
            return decorator(fn, **kwargs)

        return curried_decorator

    return wrapped_decorator
