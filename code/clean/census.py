"""The census tables, each in its own shape. A module, not a step.

data/built/census.csv holds every table one cell per row; table() gives one
back as the columns and rows of its source, Arlington's rows only for the
Bureau's county-level files, typed as a plain read would type them.
"""
import fnmatch

import paths

_cells = None


def cells():
    global _cells
    if _cells is None:
        _cells = paths.built("census")
    return _cells


def names(pattern="*") -> list:
    """The tables held, by their path under data/, matching a glob."""
    return [t for t in cells().table.unique() if fnmatch.fnmatch(t, pattern)]


def table(name):
    """One table by its path under data/, in the source's row and column order."""
    c = cells()
    d = c[c.table == name]
    if d.empty:
        raise FileNotFoundError(f"{name} is not in data/built/census.csv")
    wide = d.pivot(index="row", columns="column", values="value")
    wide = wide.loc[sorted(wide.index, key=int), list(d.column.unique())]
    wide.columns.name = None
    return paths.typed(wide.reset_index(drop=True))
