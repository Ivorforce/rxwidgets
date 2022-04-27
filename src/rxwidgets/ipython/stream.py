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
    """Map the stream by applying the underlying valuebox'd function."""
    if screen is None:
        screen = Screen()
        display(screen.widget)

    def run_fn(box: valuebox.ValueBox) -> valuebox.ValueBox:
        if not box.is_error:
            # Found a partial in a box, now run it.
            with screen():
                result = box.value()
                screen.is_loading = False

                # Got result without any errors.
                return valuebox.ValueBox(result)

            # Function raised and the error has been rendered.
            # Pass on a consequential error.
            screen.is_loading = False
            return valuebox.ValueBox(ConsequentialError(), is_error=True)

        # Found an error, either from a parameter, a defer or loading error from ourselves.

        # This will clear our screen and render any non-caught errors.
        with screen():
            try:
                box.unbox()
                # Unreachable
            except LoadingError:
                # Pass on the loading error, render nothing.
                screen.is_loading = True
                return box
            except (DeferError, ConsequentialError):
                # Render nothing, pass on the same error.
                screen.is_loading = False
                return box

        # Generic error from a previous function has been found.
        # Pass on a consequential error.
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


@optional_arg_decorator
def stream(fn: Callable, policy: parameters.Policy = 'interact', *, kwargs: dict = None) -> rx.Observable:
    fn = parameters.defaults_to_observables(fn, policy=policy, kwargs=kwargs)

    """Convert the function into a stream of results from each changing parameter."""
    def curry_fn_valueboxed(*args, **kwargs) -> valuebox.ValueBox:
        try:
            args, kwargs = valuebox.unbox_parameters(args, kwargs, strict=False)
        except Exception as e:
            # Unboxing failed; we can't run fn later. Just pass on whatever error we found.
            return valuebox.ValueBox(e, is_error=True)

        # No errors, we can run the function later.
        return valuebox.ValueBox(functools.partial(fn, *args, **kwargs))

    # Pack the function to a partial
    sig = inspect.signature(fn)
    bind = sig.bind()
    bind.apply_defaults()
    observable = rxn.call_latest(*bind.args, **bind.kwargs)(rx.just(curry_fn_valueboxed))

    return observable
