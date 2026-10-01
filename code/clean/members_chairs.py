"""Who chaired the Board each year -> data/clean/members_chairs.csv

One row per person per office per year, 1932 to 2026, from the county's own
roll (members_roster_roll.py), with the month the Board voted where the roll
gives one.

    year  office  name  since  source

`office` is `chair` or `vice-chair`, in the roster's words rather than the
roll's, which prints chairman, chairwoman, vice-chairman and, once, at 1977,
vice-president. A year has more than one row for an office where the chair
changed hands during it: 1947, when Elizabeth Magruder resigned the chair in
March and Basil DeLashmutt took it, and 1952 and 1999, where the same
happened. `since` is the month the roll dates the vote, blank for the years
it prints the office beside a name and no date - which is most years before
2003.

The chairship is a vote of the Board among its own members and says nothing
about who holds a seat, so it is kept out of members.csv, where every row is
a term. No figure reads this table yet. The question it answers - whether
the chair went to women and to members of colour in proportion to their
service - is `chair-by-race-and-gender` in docs/questions.csv, and the table
is here because the roll is read for the roster anyway and re-reading it
later would be the only alternative (docs/repository.md).
"""
import pandas as pd

import members_roster_roll as roll
from paths import write

OFFICES = {"chairman": "chair", "chairwoman": "chair", "acting chairman": "chair",
           "vice-chairman": "vice-chair", "vice-chair": "vice-chair"}

TOOK = {"took the chair": "chair", "took the vice-chair": "vice-chair"}


def build() -> pd.DataFrame:
    d = roll.rows()
    rows = []
    for _, r in d.iterrows():
        office = OFFICES.get(r.office.strip().lower())
        if office is None:
            continue
        # The roll dates the vote on the row that records it; a year that
        # prints the office and no date leaves `since` blank.
        since = r.event_date if TOOK.get(r.event) == office else ""
        rows.append({"year": int(r.year), "office": office,
                     "name": roll.name_of(r["name"]), "since": since,
                     "source": roll.SOURCE})
    out = pd.DataFrame(rows).drop_duplicates(subset=["year", "office", "name"], keep="first")
    check_one_chair(out)
    return out.sort_values(["year", "office", "since", "name"]).reset_index(drop=True)


def check_one_chair(d: pd.DataFrame):
    """A year has one chair, or says in `since` when the second took over.

    Four years have two chairs and the roll dates each change on the
    outgoing member's row rather than the incoming one's, so `since` is
    blank for the second name: 1934, after Lyman Kelley was removed in
    November; 1947, when Elizabeth Magruder resigned the chair in March;
    1952, after a court removed the chairman in September; and 1999, when
    Albert Eisenberg resigned in February. A fifth year like them would mean
    the roll had been read wrong, since it always says when a chair changed.
    """
    for (year, office), rows in d.groupby(["year", "office"]):
        if len(rows) > 1 and not (rows.since != "").any() and year not in (1934, 1947, 1952, 1999):
            raise ValueError(
                f"{year}: {len(rows)} members hold the {office} and the roll dates no "
                f"change: {sorted(rows.name)}")


if __name__ == "__main__":
    write(build(), "members_chairs")
