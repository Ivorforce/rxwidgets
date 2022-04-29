import reactivex as rx
from reactivex import operators as rxo

from rxwidgets import valuebox


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

    return rxo.flat_map(flatmap)(observable)
