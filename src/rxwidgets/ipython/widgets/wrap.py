from typing import Type, Dict

import ipywidgets.widgets
from IPython.core.display_functions import display

from .observe import subject_observing_widget
from ..stream import stream, apply
from ..flatmap import flatten


def wrap_ipywidget(Widget: Type[ipywidgets.ValueWidget]):
    def creator(*args, **kwargs):
        def create(*args, **kwargs):
            widget = Widget(*args, **kwargs)
            display(widget)
            return subject_observing_widget(widget)

        observable = stream(create)(*args, **kwargs)
        observable = apply(observable)
        observable = flatten(observable)

        return observable
    return creator


def wrap_all_valuewidgets() -> Dict:
    import inspect

    widgets = dict()
    for name, klass in ipywidgets.widgets.__dict__.items():
        if inspect.isclass(klass)\
                and issubclass(klass, ipywidgets.ValueWidget)\
                and klass is not ipywidgets.ValueWidget:
            widgets[name] = wrap_ipywidget(klass)
    return widgets
