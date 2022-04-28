from typing import Sequence

import ipywidgets
from pathlib import Path

import pandas as pd
from IPython.core.display_functions import display


def path_to_dict(path, scheme_parts):
    """
    Convert a path to a dictionary using a path scheme. The path scheme
    is also a Path-like, describing the parts of the path. Underscores are ignored.
    """
    return {
        "path": path,
        **{
            part_name: part
            for part_name, part in zip(scheme_parts, path.parts)
            if part_name != "_"
        }
    }


def select(
    paths: Sequence,
    scheme=None,
    *,
    multi=False,
    require_full_scheme=True
):
    """
    Select file paths.

    Args:
        paths: Sequence of path-likes.
        scheme: Naming scheme for attributes based from the path. Underscores (_) are
            ignored.
        multi: False to yield single rows, True to yield sub-selected dataframes.
        require_full_scheme: Ignore files that are nested in a directory not fulfilling
            to the full scheme.

    Examples:
        # Files in a folders structure like `~/my-files/team1/project1/file1.txt`.
        base_path = Path("~/my-files")
        all_paths = [
            p.relative_to(base_path)
            for p in base_path.glob("**/*.txt")
        ]
        path = rc.paths.select(all_paths, scheme="Team/Project/")

    Returns: A Voodoo stream of pandas rows or dataframes. Use select(...)['path'] to get
        a stream of just the paths.
    """
    import rxwidgets.ipython as rxi

    scheme_parts = Path(scheme).parts if scheme is not None else []
    required_path_len = len(scheme_parts) if require_full_scheme else 0
    path_parts = [name for name in scheme_parts if name != "_"]

    df = pd.DataFrame([
        path_to_dict(path, scheme_parts=scheme_parts)
        for path in map(Path, paths)
        if len(path.parts) >= required_path_len
    ], columns=['path', *path_parts])

    left_output = ipywidgets.Output()
    right_screen = rxi.Screen()
    # Display first in case errors are thrown
    display(ipywidgets.HBox(
        children=(left_output, right_screen.widget)
    ))

    with left_output:
        df_stream = rxi.pandas.dataframe.filter(
            df,
            columns=path_parts,
            search_columns=['path'],
            search_index=False
        )

    df_stream = rxi.flatten(rxi.apply(
        rxi.stream_binding(
            rxi.pandas.dataframe.select_row, df_stream,
            multi=multi,
            shown_columns=['path'],
            rows=2 + 2 * len(df.columns)
        ),
        screen=right_screen
    ))

    return df_stream
