"""Ranked Choice Virginia's tabulation by group -> data/built/survey_rcv.csv

The published table is one row per group category with three measures beside
each other. This puts it in one shape: one row per category per measure,
carrying the share, the respondents behind it and the status its preparers
gave the cell. Nothing is dropped and nothing is decided; what a `caution`
cell may be read as is settled in code/clean/survey_rcv.py.

    group        what the respondents are cut by
    category     which part of that cut
    respondents  how many respondents the category holds, every measure's base
    measure      support, awareness, understanding or net_support
    value        the weighted share, or the points for net_support
    counted      the unweighted number who answered that way
    status       ok, caution or suppressed, as rcva2026subgroups gives it
"""
import pandas as pd

from paths import RAW, source, write

TABLE = RAW / "rcva" / "survey_rcv_by_group.csv"

# Each measure's three columns in the published table. net_support carries
# points rather than a share and no count of its own.
MEASURES = {
    "support": ("support_share", "support_n", "support_status"),
    "awareness": ("awareness_share", "awareness_n", "awareness_status"),
    "understanding": ("understanding_share", "understanding_n", "understanding_status"),
    "net_support": ("net_support_points", None, "net_support_status"),
}


def build() -> pd.DataFrame:
    wide = source(TABLE, dtype=str, keep_default_na=False)
    rows = []
    for measure, (value, count, status) in MEASURES.items():
        part = pd.DataFrame({
            "group": wide["group"],
            "category": wide["category"],
            "respondents": wide["n"],
            "measure": measure,
            "value": wide[value],
            "counted": wide[count] if count else "",
            "status": wide[status],
        })
        rows.append(part)
    long = pd.concat(rows, ignore_index=True)
    if len(long) != len(wide) * len(MEASURES):
        raise AssertionError(
            f"{TABLE.name}: {len(wide)} categories and {len(MEASURES)} measures "
            f"should give {len(wide) * len(MEASURES)} rows, not {len(long)}.")
    return long.sort_values(["group", "category", "measure"],
                            kind="stable").reset_index(drop=True)


if __name__ == "__main__":
    write(build(), "survey_rcv")
