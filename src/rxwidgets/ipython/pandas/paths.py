from typing import Sequence
import reactivex as rx

import ipywidgets
from pathlib import Path

import pandas as pd
from IPython.core.display_functions import display


def paths_to_dataframe(paths: Sequence, *, scheme=None) -> pd.DataFrame:
    """
    Convert a sequence of paths to a dataframe, interpreting path parts using a scheme.
    If scheme is None, the dataframe will only have the column 'path'.
    Underscores (_) are ignored.
    """
    scheme_parts = Path(scheme).parts if scheme is not None else []
    path_parts = [name for name in scheme_parts if name != "_"]

    def path_to_dict(path):
        return {
            "path": path,
            **{
                part_name: part
                for part_name, part in zip(scheme_parts, path.parts)
                if part_name != "_"
            }
        }

    return pd.DataFrame([
        path_to_dict(path)
        for path in map(Path, paths)
        if len(path.parts) >= len(scheme_parts)
    ], columns=['path', *path_parts])


def select(
    paths: Sequence,
    scheme=None,
    *,
    multi=False,
) -> rx.Observable:
    """
    Select file paths with pandas.dataframe.filter and pandas.dataframe.select_row.

    Args:
        paths: Sequence of path-likes.
        scheme: Naming scheme for attributes based from the path. Underscores (_) are
            ignored.
        multi: False to yield single rows, True to yield sub-selected dataframes.

    Examples:
        # Files in a folders structure like `~/my-files/team1/project1/file1.txt`.
        base_path = Path("~/my-files")
        all_paths = [
            p.relative_to(base_path)
            for p in base_path.glob("**/*.txt")
        ]
        path = rc.paths.select(all_paths, scheme="Team/Project/")

    Returns: A stream of pandas rows or dataframes. Use Automap(select(...))['path'] to get
        a stream of just the paths.
    """
    import rxwidgets.ipython as rxi

    df = paths_to_dataframe(paths, scheme=scheme)

    left_output = ipywidgets.Output()
    right_screen = rxi.Screen()
    # Display first in case errors are thrown
    display(ipywidgets.HBox(
        children=(left_output, right_screen.widget)
    ))

    with left_output:
        df_stream = rxi.pandas.dataframe.filter(
            df,
            # First column is the full path
            columns=df.columns[1:],
            search_columns=['path'],
            search_index=False
        )

    df_stream = rxi.flatten(rxi.apply(
        rxi.stream(rxi.pandas.dataframe.select_row)(
            df_stream,
            multi=multi,
            shown_columns=['path'],
            rows=2 + 2 * len(df.columns)
        ),
        screen=right_screen
    ))

    return df_stream
