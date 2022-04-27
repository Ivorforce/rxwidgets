from typing import Any
import dataclasses

import ipywidgets
import reactivex as rx
from IPython.core.display_functions import display

from rxwidgets import valuebox
from rxwidgets.decorators import optional_arg_decorator

_empty = object()


class DeferError(Exception):
    pass


@dataclasses.dataclass
class Defer(rx.Observer):
    last_value: Any
    subject: rx.subject.ReplaySubject

    retrigger: bool
    hold: bool

    button: ipywidgets.ToggleButton

    def __init__(self, title: str = None, *, icon: str = None, retrigger=False, hold=False):
        super().__init__()

        self.subject = rx.subject.ReplaySubject(1)
        self.last_value = _empty

        self.retrigger = retrigger
        self.hold = hold

        if title is None:
            if hold:
                title = "Update"
            else:
                title = "Continue" if not retrigger else "Run"
        if icon is None:
            icon = "caret-right" if not hold else "rotate-right"

        self.button = ipywidgets.ToggleButton(
            description=title, value=False, icon=icon if icon else None
        )
        self.button.observe(lambda x: self.propagate() if x.new else None, 'value')
        self.button.disabled = True  # No value yet!

    def on_next(self, value: valuebox.ValueBox):
        self.last_value = value

        if self.hold:
            # Always allow clicking, even on errors - to be able to clear the bottom
            self.button.disabled = False
            self.button.value = False
            return

        self.subject.on_next(valuebox.ValueBox(DeferError(), is_error=True))
        # Only allow clicking if we don't have an error, to avoid confusion
        self.button.disabled = value.is_error
        self.button.value = value.is_error

    def on_error(self, error: Exception):
        self.subject.on_error(error)
        self.button.disabled = True
        self.button.value = False

    def on_completed(self):
        self.subject.on_completed()

    def propagate(self):
        if self.last_value is _empty:
            return

        if not self.retrigger:
            self.button.disabled = True
        else:
            self.button.value = False

        self.subject.on_next(self.last_value)


@optional_arg_decorator
def defer(observable: rx.Observable, *args, **kwargs) -> rx.subject.ReplaySubject:
    """
    Halt a stream of valueboxes, only trigger propagation when the button is pressed.
    May insert DeferErrors into the stream.

    args and kwargs are passed to `Defer`.

    Returns: A `ReplaySubject` holding the stream's latest propagated value.
    """
    defer = Defer(*args, **kwargs)

    display(defer.button)

    # FIXME
    _ = observable.subscribe(defer)

    return defer.subject
