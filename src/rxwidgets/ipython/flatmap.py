import reactivex as rx
from reactivex import operators as rxo

from rxwidgets import valuebox
from rxwidgets.ipython.parameters import as_observable


def flatten(observable: rx.Observable) -> rx.Observable:
    """
    Flatten the `rx.Observable` inside a `ValueBox` in the stream.
    """
    def flatmap(x: valuebox.ValueBox) -> rx.Observable:
        try:
            # Stream should return some usable valueboxes already, eg. through @interact
            return x.unbox()
        except:
            # Just pass down the error box
            return rx.just(x)

    # The as_observable is necessary so flat_map works on automap objects.
    # It's a little weird to have to do it but here we are.
    return rxo.flat_map(flatmap)(as_observable(observable))
