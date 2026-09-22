"""The roster: who served on the Board, and when -> data/clean/board_roster.csv

One row per person per year served, built from sources rather than delivered,
with a citation on every row. This is the backbone; demographic coding is
folded onto it separately.

Three sources, covering different periods and recording different things:

  O'Leary (2012)   1870-1915  who held each magisterial district, by election
  Novack (1994)    1930-1994  terms of service, with mid-term departures
  Alex's roster    1932-2026  person-years, delivered, source unknown

Two gaps remain, and they are left empty rather than filled by assumption:

  1916-1929  O'Leary stops at 1915; the county's candidate history has one
             1927 election and nothing before it
  1995-2026  Novack stops at 1994; after that only election results exist,
             which record who ran, not who served

Novack's terms are half-open where a member was still serving when he wrote -
"1974-" - so those run to 1994, the year of publication, and no further.
"""
import re

import pandas as pd

from files import TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"
NOVACK_PUBLISHED = 1994
YEAR = re.compile(r"(18|19|20)\d\d")


def novack_years(term):
    """Every year a term covers. 'Feb. 1990' counts 1990; '1974-' runs to 1994."""
    years = set()
    for part in term.split(";"):
        found = [int(m.group()) for m in YEAR.finditer(part)]
        if not found:
            continue
        if len(found) == 1:
            years.add(found[0])
            if part.strip().endswith("-"):
                years |= set(range(found[0], NOVACK_PUBLISHED + 1))
        else:
            years |= set(range(min(found), max(found) + 1))
    return sorted(years)


def build() -> pd.DataFrame:
    rows = []

    # --- 1870-1931, from O'Leary, already assembled per person-year ---
    early = pd.read_csv(BY_CLAUDE.parents[1] / "clean" / "board_1870-1931.csv")
    for _, r in early.iterrows():
        if r.get("elected", 1) == 0:
            continue                      # stood and lost; not a member
        rows.append({"year": int(r.year), "name": r["name"],
                     "district": r.district if pd.notna(r.district) else "",
                     "source": r.source_name})

    # --- 1930-1994, from Novack's terms of service ---
    nov = pd.read_csv(BY_CLAUDE / "arlington_historical_magazine"
                      / "novack_terms_1930-1994.csv")
    for _, r in nov.iterrows():
        for y in novack_years(str(r.term)):
            rows.append({"year": y, "name": r["name"], "district": "",
                         "source": f"Novack (1994) p.{r.page}"})

    d = pd.DataFrame(rows).drop_duplicates(["year", "name"]).sort_values(["year", "name"])
    return d.reset_index(drop=True)


if __name__ == "__main__":
    d = build()
    write(d, "board_roster")
