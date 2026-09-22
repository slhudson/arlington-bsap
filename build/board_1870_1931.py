"""Named Board members, 1870-1931 -> data/clean/board_1870-1931.csv

The person-level roster for the years Alex's roster does not reach. His starts
in 1932; before that his seat counts are bare numbers with no names behind
them, so nothing could ever be checked against them.

This is built from sources rather than delivered, and every row says where it
came from. It is meant partly as a demonstration of what the layer underneath a
roster looks like when each cell is traceable.

Two sources, doing different jobs:

  O'Leary's electoral history  who held each magisterial district, by election
  Hjerpe's paper               which of those men were Black, from 1880 census

Elections were roughly biennial in May, so each one seats a board that serves
until the next is listed. That carry-forward is an assumption, and a visible
one: O'Leary warns that elections "were not always held (or at least not
reported) when it seems that they should have occurred", so a long gap between
listed elections may mean no election or no surviving record.

Every row carries a citation in one format - author, year in parentheses, then
the locator: "O'Leary (2012) p.14", "Hjerpe (2021) Appendix 1". Neither county
document carries printed page numbers, so the page is the PDF's; full details
are in docs/sources.md.

`elected` is 1 for anyone who took the seat and 0 for anyone who stood and
lost. `basis` says how that was known: O'Leary names who *held* each district,
while the candidate history names everyone who *ran* without marking winners,
so for 1927 the highest vote in each district is taken as the winner. That is
an inference and says so.

Arlington district has no 1927 entry at all, so that seat is simply absent for
1927-1931 rather than assumed.

**Race is blank wherever nobody has established it.** For 1889-1931 that is
every row. The delivered seat counts record those years as all-White; here the
same claim appears as an empty column beside named people, which is the same
assumption made visible.
"""
import re

import pandas as pd

from files import TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"
LAST_MAGISTERIAL_YEAR = 1931   # the County Manager board takes over in 1932


def build() -> pd.DataFrame:
    seats = pd.read_csv(BY_CLAUDE / "county" / "board_1870-1920.csv")
    black = pd.read_csv(BY_CLAUDE / "hjerpe" / "black_board_members_1871-1888.csv")

    # A 1927 Board of Supervisors election appears in the candidate history.
    later = pd.read_csv(BY_CLAUDE / "county" / "candidate_history_1920-present.csv")
    later = later[later.office.str.contains("Supervisor", case=False, na=False)]

    elections = sorted(set(seats.year) | set(later.year.astype(int)))
    rows = []
    for i, year in enumerate(elections):
        ends = elections[i + 1] - 1 if i + 1 < len(elections) else LAST_MAGISTERIAL_YEAR
        ends = min(ends, LAST_MAGISTERIAL_YEAR)

        if year in set(seats.year):
            # O'Leary lists who held each district.
            block = seats[seats.year == year]
            entries = [(r.district, r.entry, f"O'Leary (2012) p.{r.page}", "held office")
                       for _, r in block.iterrows()]
        else:
            # The candidate history lists everyone who ran and does not mark
            # winners. The district is inside the office label, and the highest
            # vote in each district is taken as the winner - an inference, and
            # flagged as one.
            block = later[later.year.astype(int) == year].copy()
            block["district"] = block.office.str.extract(r"Supervisor\s+(\w+)\s+District")[0]
            block["n"] = pd.to_numeric(block.votes.astype(str).str.replace(",", ""),
                                       errors="coerce")
            best = block.groupby("district").n.transform("max")
            entries = [(r.district, r.candidate, f"Arlington County (2021) p.{r.page}",
                        "elected, inferred from highest vote" if r.n == b else "stood, not elected")
                       for (_, r), b in zip(block.iterrows(), best)]

        for district, entry, source, basis in entries:
            # The printed entry is the name plus any note about replacement or
            # vacancy. Keep both: the note is often the only record of a
            # mid-term change.
            name = re.split(r"\s*[(–-]\s*", entry, maxsplit=1)[0].strip()
            note = entry[len(name):].strip(" -–")
            surname = name.split()[-1] if name else ""
            match = black[black.surname == surname]
            race = "Black" if len(match) else ""
            source_race = match.iloc[0].evidence_location if len(match) else ""
            for served in range(year, ends + 1):
                rows.append({
                    "year": served, "district": district, "name": name,
                    "race": race, "source_race": source_race, "source_name": source,
                    "elected": 0 if basis == "stood, not elected" else 1,
                    "basis": basis, "election_year": year, "note": note,
                    "carried_forward": "" if served == year else "yes",
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    d = build()
    write(d, "board_1870-1931")
