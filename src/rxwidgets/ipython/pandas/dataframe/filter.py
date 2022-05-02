from collections import OrderedDict
from typing import List, Callable, Dict

import pandas as pd
import reactivex as rx
import ipywidgets.widgets

from rxwidgets.contexts import AnyContext
from rxwidgets.ipython.display import display

_none_selected = object()


def widget_set_options(ui: ipywidgets.widgets.widget_selection._Selection, options):
    # Unfortunately, the UI isn't good at doing this itself
    #  Can maybe remove extra checks in a future version
    if options == ui.options:
        return

    value = ui.value
    with ui.hold_sync():
        ui.options = options
        ui.value = value


def filter(
    dataframe: pd.DataFrame,
    *,
    show_reset_button=True,
    columns=...,
    search_index=True,
    search_columns=...,
) -> rx.Observable:
    """
    Filter the dataframe interactively, returning a stream of results.
    Filtering is done with search fields and dropdowns.

    Examples:
        ```
        # If streaming inputs are desired, call the function like:
        filtered_df_stream = rxi.flatten(rxi.apply(
            rxi.stream(filter_dataframe)(df_stream)
        ))
        ```
    """
    subject = rx.subject.ReplaySubject(1)
    # Will always start with the full dataframe
    subject.on_next(dataframe)

    dataframe = dataframe.copy()
    supress_changes = AnyContext()

    if search_columns is ...:
        search_columns = dataframe.columns

    if columns is ...:
        columns = dataframe.columns

    widgets = list()

    search_textfield = None
    index_textfield = None
    column_widgets = dict()

    def filtered_dataframe():
        df = dataframe
        for column, widget in column_widgets.items():
            if widget.value is not _none_selected:
                df = df[df[column] == widget.value]

        if search_textfield is not None and search_textfield.value:
            df = df[df["__search"].str.contains(search_textfield.value)]

        if index_textfield is not None and index_textfield.value:
            df = df[df["__index_search"].str.contains(index_textfield.value)]

        return df.drop(columns=["__search", "__index_search"], errors='ignore')

    def on_change(change=None):
        if supress_changes:
            return
        subject.on_next(filtered_dataframe())

    if search_columns is not None:
        dataframe["__search"] = dataframe[search_columns].astype(str).apply(
            (lambda x: "\t".join(x)), axis=1
        )

        search_textfield = ipywidgets.Text(description="Search")
        search_textfield.observe(on_change, 'value')
        widgets.append(search_textfield)

    if search_index:
        dataframe["__index_search"] = index_as_string = dataframe.index.astype(str)

        index_name = dataframe.index.name or "Index"
        index_textfield = ipywidgets.Combobox(
            description=index_name,
            options=list(index_as_string)
        )
        index_textfield.observe(on_change, 'value')
        widgets.append(index_textfield)

    if len(columns) > 0:
        column_widgets = make_column_widgets(dataframe, columns=columns, on_change=on_change)
        widgets.extend(column_widgets.values())

    if show_reset_button:
        reset_button = ipywidgets.Button(
            description="Reset Filter",
            layout={'width': "300px"},
            disabled=True
        )

        def reset():
            with supress_changes:
                if search_textfield is not None:
                    search_textfield.value = ""
                if index_textfield is not None:
                    index_textfield.value = ""
                for widget in column_widgets:
                    widget.value = _none_selected
            on_change()

        reset_button.on_click(reset)
        widgets = [reset_button, *widgets]

    vbox = ipywidgets.VBox(children=widgets)
    display(vbox)

    return subject


def make_column_widgets(
    dataframe: pd.DataFrame,
    *,
    columns: List[str],
    on_change=Callable
) -> Dict[str, ipywidgets.Dropdown]:
    missing_columns = set(columns).difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Columns not in dataframe: {missing_columns}")

    column_dropdowns: Dict[str, ipywidgets.Dropdown] = OrderedDict()
    is_updating_context = AnyContext()

    def filtered_dataframe(*, but: str = None):
        df = dataframe
        for column, widget in column_dropdowns.items():
            if widget.value is _none_selected or column == but:
                continue

            df = df[df[column] == widget.value]
        return df

    def update_dropdown_options():
        for column, dropdown in column_dropdowns.items():
            df_filtered = filtered_dataframe(but=column)
            options = sorted(set(df_filtered[column]))

            widget_set_options(dropdown, options=[
                ("/", _none_selected),
                *((str(val), val) for val in options)
            ])

    def on_dropdown_change(change):
        if is_updating_context:
            return

        with is_updating_context:
            update_dropdown_options()

        on_change(change)

    for column in columns:
        dropdown = ipywidgets.Dropdown(
            options=[_none_selected],
            value=_none_selected,
            description=column
        )
        dropdown.observe(on_dropdown_change)
        column_dropdowns[column] = dropdown
    update_dropdown_options()

    return column_dropdowns
