import reactivex as rx

from rxwidgets.ipython.stream import stream_defaults, apply


def print_stream(observable: rx.Observable) -> rx.Observable:
    """
    Convenient way to print / display the contents of a stream.
    """
    @apply
    @stream_defaults
    def run(x=observable):
        print(x)

    return run
