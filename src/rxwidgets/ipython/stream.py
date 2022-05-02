import functools
import inspect
from typing import Callable

import reactivex as rx
import reactivex.operators as rxo
from IPython.core.display_functions import display

from rxwidgets import rx as rxn, valuebox
from rxwidgets.decorators import optional_arg_decorator
from . import parameters

from .load import LoadingError
from .screen import Screen
from .defer import DeferError


class ConsequentialError(Exception):
    pass


@optional_arg_decorator
def apply(observable: rx.Observable, *, screen: Screen = None) -> rx.Observable:
    """
    Map the stream by applying the underlying valuebox'd function.

    Args:
        observable: A stream of `ValueBox(Callable[[], Any])`
        screen: If provided, apply the function in this screen.
    """
    if screen is None:
        screen = Screen()
        display(screen.widget)

    def run_fn(box: valuebox.ValueBox) -> valuebox.ValueBox:
        with screen():
            try:
                fn = box.unbox()
                result = fn()
                screen.is_loading = False

                # Got result without any errors.
                return valuebox.ValueBox(result)
            except LoadingError:
                # Pass on the loading error, render nothing. If not yet, show loading indicator.
                screen.is_loading = True
                return box
            except (DeferError, ConsequentialError):
                # Pass on the error, render nothing.
                screen.is_loading = False
                return box

        # Either the function, or the unboxing, raised and the error has been rendered.
        # Now pass on a consequential error.
        screen.is_loading = False
        return valuebox.ValueBox(ConsequentialError(), is_error=True)

    # Run the function, gathering results in a subject
    observable = rxo.map(run_fn)(observable)

    subject = rx.subject.ReplaySubject(1)
    # FIXME
    _ = observable.subscribe(subject)

    def on_error(error: Exception):
        with screen():
            print("Stream failed; disposing.")
            raise error from None

    # FIXME
    _ = subject.subscribe(on_error=on_error)

    return subject


def curry_fn_valueboxed(fn, *args, **kwargs) -> valuebox.ValueBox:
    """
    Curry the function (using `functools.partial`) such that it can be applied without parameters.
    Parameters are assumed to be `ValueBox`, or are converted thereto.
    Wrap the resulting partial in a ValueBox.
    """
    try:
        args, kwargs = valuebox.unbox_parameters(args, kwargs, strict=False)
    except Exception as e:
        # Unboxing failed; we can't run fn later. Just pass on whatever error we found.
        return valuebox.ValueBox(e, is_error=True)

    # No errors, we can run the function later.
    return valuebox.ValueBox(functools.partial(fn, *args, **kwargs))


@optional_arg_decorator
def stream_defaults(fn: Callable, policy: parameters.Policy = 'interact', kwargs: dict = None) -> rx.Observable:
    """
    Convert all parameters to streams and create an `rx.Observable` yielding results of `call_latest`.

    Args:
        fn: The function to stream.
        policy: Policy for `parameters.defaults_to_observables`.
        kwargs: Overrides or additions for the defaults.

    Returns: `rx.Observable` containing `ValueBox` instances with results of the function.
    """
    fn = parameters.defaults_to_observables(fn, policy=policy, kwargs=kwargs)

    # Pack the function to a partial
    sig = inspect.signature(fn)
    bind = sig.bind()
    bind.apply_defaults()
    observable = rxn.call_latest(
        rx.just(fn), *bind.args, **bind.kwargs
    )(rx.just(curry_fn_valueboxed))

    return observable


def stream(fn: Callable, policy: parameters.Policy = 'just') -> Callable:
    """
    Convert all arguments to streams and create an `rx.Observable` yielding results of `call_latest`.
    This will use the 'just' policy of `parameters.defaults_to_observables`.

    Returns: `rx.Observable` containing `ValueBox` instances with results of the function.
    """
    as_observable = functools.partial(parameters.as_observable, policy=policy)
    just_fn = rx.just(fn)
    just_curry_fn = rx.just(curry_fn_valueboxed)

    @functools.wraps(fn)
    def wrapped(*args, **kwargs) -> rx.Observable:
        return rxn.call_latest(
            just_fn,
            *map(as_observable, args),
            **{key: as_observable(val, name=key) for key, val in kwargs.items()}
        )(just_curry_fn)

    return wrapped
