"""Ranked Choice Virginia's tabulation by group -> data/built/survey_rcv.csv

The published table already holds one row per group category per answer, so
this step renames its columns to the ones this repository uses and carries
every row. What a cell its preparers marked `caution` may be read as is
settled in code/clean/survey_rcv.py.

    question     what was asked
    group        what the respondents are cut by
    category     which part of that cut
    answer       the answer option, or a rollup of several, or a net
    kind         answer, rollup or net
    respondents  how many the category holds, the base for every share
    counted      how many gave this answer
    value        the weighted share, or points where the measure is a net
    unit         share or points
    status       ok, caution or suppressed, as rcva2026subgroups gives it
"""
from paths import RCVA, source, write

TABLE = RCVA / "survey_rcv_answers_by_group.csv"

COLUMNS = {"question": "question", "group": "group", "category": "category",
           "measure": "answer", "kind": "kind", "base_n": "respondents",
           "n": "counted", "weighted_share": "value", "unit": "unit",
           "status": "status"}


def build():
    d = source(TABLE, dtype=str, keep_default_na=False)
    missing = set(COLUMNS) - set(d.columns)
    if missing:
        raise AssertionError(f"{TABLE.name} is missing {sorted(missing)}")
    return d[list(COLUMNS)].rename(columns=COLUMNS)


if __name__ == "__main__":
    write(build(), "survey_rcv")
