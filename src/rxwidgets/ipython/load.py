import reactivex as rx
import reactivex.operators as rxo

from rxwidgets import valuebox


class LoadingError(Exception):
    pass


def long(observable: rx.Observable) -> rx.Observable:
    """
    On every non-error valuebox in a stream, first send a LoadingError.
    """
    def load_error_first(x: valuebox.ValueBox):
        if x.is_error:
            # No load if we are just going to show an error on run.
            return rx.just(x)

        return rx.of(
            valuebox.ValueBox(LoadingError(), is_error=True),
            x,
        )

    return rxo.flat_map(load_error_first)(observable)
