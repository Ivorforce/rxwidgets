from typing import Callable

import reactivex as rx
import rxwidgets.rx as rxn
from rxwidgets import valuebox
from rxwidgets.delegating import delegating
from rxwidgets.ipython.parameters import as_observable


def decorate(fn: Callable) -> Callable:
    just_fn = rx.just(valuebox.function(fn, strict=False))

    def wrapped(*args, **kwargs):
        args = [as_observable(x) for x in args]
        kwargs = {key: as_observable(val) for key, val in kwargs.items()}
        return Voodoo(rxn.call_latest(*args, **kwargs)(just_fn))

    return wrapped


@delegating(decorator=decorate, include_reverse=True)
class Voodoo(rx.abc.ObservableBase):
    """
    Represents objects _inside_ an observable: All operations to this object result in operations applied as a map to a stream.
    Inputs are interpreted as non-interactive observables, preferably containing valuebox'd streams.

    Examples:
        ```
        import valuebox
        import reactivex as rx

        x = rx.just(valuebox.ValueBox(5))
        y = rx.just(valuebox.ValueBox(2))

        # Voodoo
        import rxwidgets.ipython as rxi
        z = rxi.Voodoo(x) + y

        # Without Voodoo
        import operator
        z = rxn.call_latest(x, y)(
            rx.just(valuebox.function(operator.add, strict=False))
        )
        ```
    """
    def __init__(self, observable):
        if isinstance(observable, Voodoo):
            self.__observable__ = observable.stream
        elif isinstance(observable, rx.Observable):
            self.__observable__: rx.Observable = observable
        else:
            raise ValueError(f"Not an observable: {observable}")

    @property
    def stream(self) -> rx.Observable:
        return self.__observable__

    def subscribe(self, *args, **kwargs) -> rx.abc.DisposableBase:
        return self.stream.subscribe(*args, **kwargs)

    def pipe(self, *args):
        return Voodoo(rx.pipe(self.stream, *args))
