import dataclasses
from contextlib import contextmanager

import ipywidgets


@dataclasses.dataclass
class Screen:
    """
    A widget (container) capable of displaying function outputs and load states.
    """
    widget: ipywidgets.VBox = None

    output: ipywidgets.Output = None
    loading_widget: ipywidgets.HTML = None

    _is_loading = False

    def __init__(self, loading_html='<i class="fas fa-circle-notch fa-spin fa-3x">'):
        self.output = ipywidgets.Output()
        self.loading_widget = ipywidgets.HTML(value=loading_html)
        self.loading_widget.layout.display = 'none'

        self.widget = ipywidgets.VBox(children=(self.output, self.loading_widget))

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @is_loading.setter
    def is_loading(self, is_loading: bool):
        self.loading_widget.layout.display = 'block' if is_loading else 'none'
        self._is_loading = bool(is_loading)

    @contextmanager
    def __call__(self):
        self.output.clear_output(wait=True)

        with self.output:
            yield
            # zero-width space, if nothing was printed this clears the output
            print(end="\u200b")

    def clear(self):
        self.output.clear_output()
