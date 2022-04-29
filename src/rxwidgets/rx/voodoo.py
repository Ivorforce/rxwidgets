import operator
from typing import Callable, Any

import reactivex as rx

from .call import call_latest


class VoodooObservable(rx.abc.ObservableBase):
    """
    An object wrapping a stream that will map each of its operations to the objects in the stream.

    Examples:
        ```
        x = VoodooObservable(rx.just(5)) * 2 + 5
        # is the same as
        rx.just(5).pipe(
            rx.map(lambda x: x * 2),
            rx.map(lambda x: x + 5)
        )
        ```
    """

    def __init__(
        self,
        stream: rx.abc.ObservableBase,
        call: Callable[[Callable], Callable] = None,
        to_observable: Callable[[Any], rx.Observable] = None,
    ):
        """
        Args:
            stream: The stream to wrap.
            call: Decorator for functions.
            to_observable: A function to convert an argument to an observable.
        """
        self.__stream__ = stream.stream if isinstance(stream, VoodooObservable) else stream
        self.__caller__ = call
        self.__to_observable__ = to_observable

    def subscribe(self, *args, **kwargs) -> rx.abc.DisposableBase:
        return self.stream.subscribe(*args, **kwargs)

    @property
    def stream(self):
        return self.__stream__

    def pipe(self, *args):
        return VoodooObservable(
            self.__stream__.pipe(*args),
            call=self.__caller__,
            to_observable=self.__to_observable__,
        )

    def map(self, fn, *args, **kwargs):
        args = map(self.__maybe_to_observable__, args)
        kwargs = {key: self.__maybe_to_observable__(val) for key, val in kwargs.items()}

        return VoodooObservable(
            call_latest(*args, **kwargs)(rx.just(fn))
            if self.__caller__ is None else
            call_latest(*args, **kwargs)(rx.just(self.__caller__(fn))),
            call=self.__caller__,
            to_observable=self.__to_observable__,
        )

    def __maybe_to_observable__(self, x):
        return self.__to_observable__(x) if self.__to_observable__ is not None else x

    def __getattr__(self, name) -> 'VoodooObservable':
        return self.map(getattr, self.stream, name)

    def __call__(self, *args, **kwargs):
        return self.map(self.stream, *args, **kwargs)


# Register All Operators

def _monkey_patch_operators():
    def make_operator(fn: Callable, reverse=False):
        def function(self: VoodooObservable, *args):
            args = (self.stream, *args)

            return self.map(
                fn,
                *(args[::-1] if reverse else args)
            )

        return function

    operators = set(filter(lambda op: op.startswith('__'), dir(operator)))
    operators -= {'__name__'}

    for fn_name in operators:
        fn = getattr(operator, fn_name)

        setattr(VoodooObservable, fn_name, make_operator(fn))

        # register also the reverse version, eg. __radd__
        # TODO this of course registers a bunch of nonsense like __rabs__.
        reverse_fn_name = f'__r{fn_name[2:]}'
        setattr(VoodooObservable, reverse_fn_name, make_operator(fn, reverse=True))


_monkey_patch_operators()
