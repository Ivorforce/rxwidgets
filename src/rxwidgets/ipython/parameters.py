import functools
import inspect
from typing import Callable, List, Tuple, Optional, Any, Literal

import reactivex as rx
import ipywidgets
from IPython.display import display
from ipywidgets import interactive

from rxwidgets.decorators import optional_arg_decorator

Policy = Literal['just', 'interact']


def as_observable(x, name: str = None, *, policy: Policy = 'just') -> rx.Observable:
    """
    Convert x to an observable, raising if impossible.

    Args:
        x: The object to convert.
        name: The name to use, if the policy requires.
        policy: The policy to use for ambiguous objects.

    Raises:
        `ValueError` on inconvertible objects.

    Returns: An observable.
    """
    from .widgets import subject_observing_widget
    from .automap import Automap

    if isinstance(x, ipywidgets.ValueWidget):
        display(x)
        return subject_observing_widget(x)

    if isinstance(x, Automap):
        return x.observable

    if isinstance(x, rx.Observable):
        return x

    if policy == 'just':
        return rx.just(x)
    elif policy == 'interact':
        if name is None:
            raise ValueError("Cannot convert to interactive widget without a name.")

        def mock_function(x):
            pass

        # Create a new signature with the original signature
        #   but just one parameter with replaced default
        changed_param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=x)
        new_sig = inspect.Signature(parameters=(changed_param,))
        mock_function.__signature__ = new_sig

        vbox = interactive(mock_function)
        widget = vbox.children[0]

        display(widget)
        return subject_observing_widget(widget)
    else:
        raise ValueError(f"Unknown Policy: {policy}")


@optional_arg_decorator
def defaults_to_observables(fn: Callable, policy: Policy = 'interact', *, kwargs: dict = None) -> Callable:
    """
    Convert defaults of the function to observables.

    Args:
        fn: The function to modify
        policy: The policy to apply for ambiguous objects.
        kwargs: Overrides for any parameter defaults for conversion.

    Raises:
        `ValueError` on inconvertible objects.

    Returns: A version of the function with the same arguments, but defaults changed to all `rx.observable`.
    """
    kwargs = kwargs or dict()

    sig = inspect.signature(fn)
    # Just a sanity check that no unknown kwargs have been passed
    sig.bind_partial(**kwargs)
    fn_copy = functools.partial(fn)

    fn_copy.__signature__ = sig.replace(
        parameters=(
            param.replace(default=as_observable(kwargs.get(param.name, param.default), name=param.name, policy=policy))
            for name, param in sig.parameters.items()
            if param.default is not inspect._empty
        )
    )

    return fn_copy
