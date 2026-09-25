"""Arlington's vote by party, for President and for the County Board -> data/clean/voters.csv

One row per election and office: votes for Democratic, Republican, ABC and
other candidates, votes for candidates the source gives no label, the total,
and a source per row. `office` is "president" (every fourth year from 1872)
or "county board" (every year from 1931).

A County Board candidate is counted under the label the county's record
prints after their name, not under the party board_members.csv attaches to
the winner. A year whose returns are not the county's whole vote is marked
incomplete, on the rule in elections.contest_rows(). docs/voters.md has
the reasoning.

Two sources for the presidential vote, joined at 1924:

  oleary2010     1872-1920   the county's returns as O'Leary compiled them;
                             party is the nominee's, named in NOMINEES
  vaelections    1924-2024   the state's canvassed locality totals

The years in INCOMPLETE are kept but marked so. The county's own
presidential returns are read as a check on the state's, and the build
reports the years they differ by more than TOLERANCE.
"""
import re

import pandas as pd

import citekeys
import elections
from elections import COUNTY_HISTORY_THROUGH
from paths import RAW, TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"
OLEARY = BY_CLAUDE / "arlington_county" / "president_1872-1920.csv"
STATE = RAW / "va_dept_of_elections" / "president_1924-2024.csv"

# The major-party nominees, (Democratic, Republican), as O'Leary spells them.
NOMINEES = {
    1872: ("Greeley", "Grant"), 1876: ("Tilden", "Hayes"), 1880: ("Hancock", "Garfield"),
    1884: ("Cleveland", "Blaine"), 1888: ("Cleveland", "Harrison"), 1892: ("Cleveland", "Harrison"),
    1896: ("Bryan", "McKinley"), 1900: ("Bryan", "McKinley"), 1904: ("Parker", "Roosevelt"),
    1908: ("Bryan", "Taft"), 1912: ("Wilson", "Taft"), 1916: ("Wilson", "Hughes"),
    1920: ("Cox", "Harding"),
}
INCOMPLETE = {1896: "Washington district and the total are printed '?'",
              1904: "O'Leary: the returns 'appear incomplete'",
              1908: "O'Leary: the returns 'appear incomplete'"}
LINE = re.compile(r"^(?P<name>[A-Za-z.'’ /]+?)(?:\s*\([^)]*\))?\s+(?P<counts>[\d,? ]+)$")
TOLERANCE = 0.05
BANDS = ["dem", "rep", "abc", "other", "unrecorded"]
# What the county's labels record (elections.LABELS) and the band each
# vote counts in.
BAND = {"Democratic": "dem", "Republican": "rep", "ABC": "abc",
        "independent": "other", "other": "other", "": "unrecorded"}


def oleary() -> pd.DataFrame:
    d = pd.read_csv(OLEARY)
    rows = []
    for year, g in d.groupby("year"):
        dem, rep = NOMINEES[int(year)]
        votes = {"dem": 0, "rep": 0, "other": 0}
        for _, r in g.iterrows():
            m = LINE.match(r.entry.strip())
            if not m:
                continue                              # prose, e.g. "(reported that McKinley won ..."
            counts = [c for c in m.group("counts").split() if c != "?"]
            if not counts:
                continue
            total = int(counts[-1].replace(",", ""))   # the last figure is the county total
            surname = m.group("name").split("/")[0].strip()
            if surname == dem:
                votes["dem"] += total
            elif surname == rep:
                votes["rep"] += total
            elif surname in NOMINEES[int(year)]:
                raise AssertionError(f"{year}: {surname} matched twice")
            else:
                votes["other"] += total
        if votes["dem"] == 0 and votes["rep"] == 0:
            raise ValueError(f"{year}: no line matched either nominee {NOMINEES[int(year)]}")
        rows.append({"year": int(year), **votes,
                     "total": sum(votes.values()),
                     "complete": int(year) not in INCOMPLETE,
                     "source": f"{citekeys.OLEARY} p.{g.page.iloc[0]}",
                     "note": INCOMPLETE.get(int(year), "")})
    return pd.DataFrame(rows)


def state() -> pd.DataFrame:
    s = pd.read_csv(STATE, low_memory=False)
    s = s[~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)].copy()
    s["year"] = pd.to_datetime(s.election_date).dt.year
    s["band"] = s.candidate_party_name.map({"Democratic": "dem", "Republican": "rep"}).fillna("other")
    g = s.pivot_table(index=["year", "contest_id"], columns="band", values="votes", aggfunc="sum",
                      fill_value=0).reset_index()
    g["total"] = g[["dem", "rep", "other"]].sum(axis=1)
    g["complete"] = True
    g["source"] = [f"{citekeys.VA_ELECTIONS} contest {c}" for c in g.contest_id]
    g["note"] = ""
    return g[["year", "dem", "rep", "other", "total", "complete", "source", "note"]]


def county_check(d: pd.DataFrame):
    """The county's own presidential returns, against the state's."""
    c = elections.county_history(office=re.compile("^President"))
    c = c[c.candidate.str.contains(r"\((?:D|R)\s?\)$")].copy()
    c["band"] = c.candidate.str.extract(r"\((D|R)\s?\)$")[0].map({"D": "dem", "R": "rep"})
    county = c.groupby(["year", "band"]).votes.sum().unstack()
    both = d.set_index("year")[["dem", "rep"]].join(county, rsuffix="_county", how="inner")
    off = both[((both.dem - both.dem_county).abs() / both.dem > TOLERANCE)
               | ((both.rep - both.rep_county).abs() / both.rep > TOLERANCE)]
    if not off.empty:
        print("  voters.csv: county and state disagree by more than "
              f"{TOLERANCE:.0%} in {list(off.index)} (state figures kept)")


def county_board_county() -> pd.DataFrame:
    """1931-2021 from the county's candidate history: every general and
    special County Board contest in a year, summed; primaries and write-ins
    left out."""
    c = elections.county_history()
    c = c[~c.primary]
    rows = []
    for year, g in c.groupby("year"):
        named, complete, note = elections.contest_rows(g)
        counts = dict.fromkeys(BANDS, 0)
        for _, r in named[named.person & named.votes.notna()].iterrows():
            label = elections.label_of(r.candidate, where=f"{year}: ")
            counts[BAND[elections.LABELS[label]] if label else "unrecorded"] += int(r.votes)
        rows.append({"year": int(year), "office": "county board", **counts,
                     "total": sum(counts.values()), "complete": complete,
                     "source": f"{citekeys.ARLINGTON_ELECTIONS} p.{named.page.iloc[0]}",
                     "note": note})
    return pd.DataFrame(rows)


def county_board_state() -> pd.DataFrame:
    """2022 on from the state database. Its general-election rows carry a
    party through 2022 and none after; a candidate who won that year's
    Democratic primary is counted Democratic, and the rest are unrecorded."""
    s = elections.state_results()
    s = s[s.person & (s.year > COUNTY_HISTORY_THROUGH)]
    won_primary = s[s.election_type.str.startswith("Primary") & (s.primary_party == "Democratic")
                    & s.is_winner]
    dem_primary = set(zip(won_primary.year, won_primary.surname))
    general = s[s.election_type.str.startswith("General")].copy()
    general["band"] = [
        "dem" if p == "Democratic" or (y, n) in dem_primary
        else "rep" if p == "Republican" else "other" if isinstance(p, str) else "unrecorded"
        for p, y, n in zip(general.candidate_party_name, general.year, general.surname)]
    rows = []
    for year, g in general.groupby("year"):
        counts = g.groupby("band").votes.sum().reindex(BANDS, fill_value=0)
        rows.append({"year": int(year), "office": "county board", **counts.astype(int).to_dict(),
                     "total": int(counts.sum()), "complete": True,
                     "source": f"{citekeys.VA_ELECTIONS} contest " + ", ".join(str(c) for c in sorted(g.contest_id.unique())),
                     "note": "party from the Democratic primary; the general carries none"
                             if g.candidate_party_name.isna().all() else ""})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    pres = pd.concat([oleary(), state()], ignore_index=True)
    pres["office"] = "president"
    pres["abc"] = 0
    pres["unrecorded"] = 0
    years = sorted(pres.year)
    assert years == list(range(1872, 2025, 4)), f"not every fourth year 1872-2024: {years}"
    county_check(pres)
    board = pd.concat([county_board_county(), county_board_state()], ignore_index=True)
    years = sorted(board.year)
    # Four-year terms for the whole Board in 1931 and 1935; one seat a year from 1939.
    assert years == [1931, 1935] + list(range(1939, 2026)), f"County Board elections are not 1931, 1935, then every year: {years}"
    d = pd.concat([pres, board], ignore_index=True)
    cols = ["year", "office", *BANDS, "total", "complete", "source", "note"]
    d = d[cols].sort_values(["office", "year"], ascending=[False, True]).reset_index(drop=True)
    assert (d.total == d[BANDS].sum(axis=1)).all(), "bands do not sum to the total"
    return d


if __name__ == "__main__":
    write(build(), "voters")
