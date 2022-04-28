import reactivex as rx
from enum import Enum

import ipywidgets.widgets
import pandas as pd
from IPython.display import display

from rxwidgets import valuebox
from rxwidgets.ipython import DeferError


def _row_to_label(row):
    def format_value(value):
        if isinstance(value, Enum):
            return value.name
        return str(value)
    return "    ".join(row.apply(format_value)) + "    "


def select_row(
    dataframe: pd.DataFrame,
    *,
    descripton="",
    multi=False,
    rows=15,
    max_rows=1000,
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
            rxi.stream_binding(select_row, df_stream)
        ))
        ```
    """

    if max_rows is not None:
        dataframe = dataframe.iloc[:max_rows]

    if shown_columns is None:
        shown_columns = dataframe.columns

    options = [
        (row_to_label(row), index)
        for index, row in dataframe[shown_columns].iterrows()
    ]

    Component = ipywidgets.SelectMultiple if multi else ipywidgets.Select
    select: ipywidgets.widgets.widget_selection._Selection = Component(
        description=descripton,
        options=options,
        rows=rows,
        layout={'width': 'max-content'}
    )

    subject = rx.subject.ReplaySubject(1)

    def on_select(selected):
        if multi:
            selected = [s for s in selected if s is not None]

        if selected is None:
            subject.on_next(valuebox.ValueBox(DeferError(), is_error=True))
            return

        subject.on_next(valuebox.ValueBox(dataframe.loc[selected, :]))

    select.observe(lambda change: on_select(change.new), 'value')
    on_select(select.value)

    display(select)

    return subject