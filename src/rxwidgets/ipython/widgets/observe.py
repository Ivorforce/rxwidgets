import reactivex as rx

import ipywidgets


def subject_observing_widget(widget: ipywidgets.ValueWidget):
    subject = rx.subject.ReplaySubject(1)

    def on_change(change):
        subject.on_next(change.new)

    widget.observe(on_change, 'value')
    subject.on_next(widget.value)

    return subject
