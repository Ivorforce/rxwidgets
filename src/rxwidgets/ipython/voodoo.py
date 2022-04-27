import functools

import reactivex as rx
import rxwidgets.rx as rxn
from rxwidgets import valuebox
from rxwidgets.ipython.parameters import as_observable


def voodoo(subject: rx.Observable) -> rxn.VoodooObservable:
    return rxn.VoodooObservable(
        subject,
        call=functools.partial(valuebox.function, strict=False),
        to_observable=as_observable
    )
