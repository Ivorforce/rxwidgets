import reactivex as rx
from enum import Enum

import ipywidgets.widgets
import pandas as pd
from IPython.display import display

from rxwidgets import valuebox
from rxwidgets.ipython import DeferError


_hidden_rows = object()


def _row_to_label(row):
    def format_value(value):
        if isinstance(value, Enum):
            return value.name
        return str(value)
    return "    ".join(row.apply(format_value)) + "    "


def select_row(
    dataframe: pd.DataFrame,
    *,
    description="",
    multi=False,
    rows=15,
    max_rows=500,
    shown_columns=None,
    row_to_label=_row_to_label,
):
    """
    Filter the dataframe interactively, returning a stream of results.
    Filtering is done by selecting rows.

    Examples:
        ```
        # If streaming inputs are desired, call the function like:
        filtered_df_stream = rxi.flatten(rxi.apply(
            rxi.stream(select_row)(df_stream)
        ))
        ```
    """
    min = max = None
    if isinstance(multi, bool):
        pass
    elif isinstance(multi, int):
        min = multi
        multi = True
    elif isinstance(multi, tuple):
        min, max = multi
        multi = True

    hidden_rows = None
    shown_rows = dataframe.index
    if max_rows is not None and len(dataframe) > max_rows + 1:
        hidden_rows = dataframe.index[max_rows:]
        shown_rows = dataframe.index[:max_rows]

    if shown_columns is None:
        shown_columns = dataframe.columns

    options = [
        (row_to_label(row), index)
        for index, row in dataframe[shown_columns].loc[shown_rows].iterrows()
    ]
    if hidden_rows is not None:
        options.append((f"... {len(hidden_rows)} more", _hidden_rows))

    Component = ipywidgets.SelectMultiple if multi else ipywidgets.Select
    select: ipywidgets.widgets.widget_selection._Selection = Component(
        description=description,
        options=options,
        rows=rows,
        layout={'width': 'max-content'}
    )

    subject = rx.subject.ReplaySubject(1)

    def on_select(selected):
        if selected is None:
            subject.on_next(valuebox.ValueBox(DeferError(), is_error=True))
            return

        if multi:
            if selected and selected[-1] is _hidden_rows:
                selected = [*selected[:-1], *hidden_rows]

            if (min is not None and len(selected) < min) or (max is not None and len(selected) > max):
                subject.on_next(valuebox.ValueBox(DeferError(), is_error=True))
                return
        else:
            if selected is _hidden_rows:
                # Can't select a multi row in a single selection widget.
                subject.on_next(valuebox.ValueBox(DeferError(), is_error=True))

        subject.on_next(valuebox.ValueBox(dataframe.loc[selected, :]))

    select.observe(lambda change: on_select(change.new), 'value')
    on_select(select.value)

    display(select)

    return subject
