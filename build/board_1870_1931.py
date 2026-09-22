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

The `basis` column separates the two. O'Leary names who *held* each district;
the candidate history names everyone who *ran*, without marking winners. Six
candidates appear for three seats in 1927 for that reason, and they are not
evidence that six people served.

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
            # The candidate history lists everyone who ran, winners not marked,
            # so these are candidates rather than confirmed office-holders.
            block = later[later.year.astype(int) == year]
            entries = [("", r.candidate, f"Arlington County (2021) p.{r.page}", "candidate only")
                       for _, r in block.iterrows()]

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
                    "basis": basis, "elected": year, "note": note,
                    "carried_forward": "" if served == year else "yes",
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    d = build()
    write(d, "board_1870-1931")
