import reactivex as rx
import rxwidgets.rx as rxn
from rxwidgets import valuebox
from rxwidgets.ipython.parameters import as_observable


def voodoo(subject: rx.Observable) -> rxn.VoodooObservable:
    """Wrap the observable in a `VoodooObservable` compatible with valuebox streams."""
    return rxn.VoodooObservable(
        subject,
        call=valuebox.function(strict=False),
        to_observable=as_observable
    )
