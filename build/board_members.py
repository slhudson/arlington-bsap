"""raw/ member database -> data/board_members.csv

One row per member per year, 1932-2026. Person-level, where board_seats.csv is
year-level, and the two cover different periods. See docs/questions.md.

No figure uses this yet. It is built so the descriptive coding has a home, and
so a source column can be added per docs/sources.md recording what backs each
race and gender assignment.
"""
import pandas as pd

from files import BOARD_MEMBERS_XLSX, write


def build() -> pd.DataFrame:
    r = pd.read_excel(BOARD_MEMBERS_XLSX)
    r.columns = [c.strip().lower().replace("/", "_") for c in r.columns]

    # A person should appear once per year. Alfred Frisbie has three rows for
    # 1952 - the coding agrees across them, so nothing is miscoded, but any
    # tally built from this file would count him three times. Recorded rather
    # than silently deduplicated: raw/ and by_human/ are not edited here.
    key = ["year", "last_name", "first_name"]
    dup = r[r.duplicated(key, keep=False)]
    known = {(1952, "Frisbie", "Alfred")}
    found = {tuple(v) for v in dup[key].drop_duplicates().values}
    unexpected = found - known
    assert not unexpected, f"new duplicate person-years: {sorted(unexpected)}"

    # Where the coding differs between duplicate rows, a tally is ambiguous.
    for k, grp in dup.groupby(key):
        for c in ["woman", "white", "black", "hispanic_latino"]:
            assert grp[c].nunique() <= 1, f"{k} duplicate rows disagree on {c}"
    return r


if __name__ == "__main__":
    write(build(), "board_members")
