from rxwidgets.ipython.stream import apply, stream_defaults
from rxwidgets.ipython.defer import defer

from .automap import Automap


def interact(fn, **kwargs) -> Automap:
    """
    Convenience function to ease the transition from `ipywidgets.interact`.

    If you want to add more sophisticated functionality, like pre-loading
    for slow functions or customized run buttons, use this instead:

    ```
    @rxi.apply
    @rxi.stream_defaults
    def fn(...):
        pass
    ```

    Examples:
        ```
        @rxi.interact
        def fn(...):
            pass
        ```
    """
    observable = stream_defaults(fn, policy='interact', kwargs=kwargs)
    observable = apply(observable)

    return Automap(observable)


def interact_manual(fn, **kwargs) -> Automap:
    """
    Convenience function to ease the transition from `ipywidgets.interact_manual`.

    If you want to add more sophisticated functionality, like pre-loading
    for slow functions or customized run buttons, use this instead:
    ```
    @rxi.apply
    @rxi.defer
    @rxi.stream_defaults
    def fn(...):
        pass
    ```

    Examples:
        ```
        @rxi.interact_manual
        def fn(...):
            pass
        ```
    """
    observable = stream_defaults(fn, policy='interact', kwargs=kwargs)
    observable = defer(observable)
    observable = apply(observable)

    return Automap(observable)
