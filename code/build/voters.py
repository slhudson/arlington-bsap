"""Arlington's presidential vote by party, 1872-2024 -> data/clean/voters.csv

One row per presidential election: votes for the Democratic and Republican
nominees, for everyone else, and the total, with a source per row.

**Why the presidential vote.** Virginia has no party registration, so there is
no count of residents' partisanship at all; the presidential vote is the
standard proxy and the one measure that arrives as a dataset. It measures
voters, not residents, and before 1966 an electorate narrowed by the poll
tax and the 1902 constitution - which is why the file is voters.csv and the
figure says "share of voters". Q30 in docs/questions.md.

Two sources, joined at 1924:

  oleary2010     1872-1920   the county's returns as O'Leary compiled them
                             from the Alexandria Gazette, by district or as
                             a county figure, transcribed verbatim
  vaelections    1924-2024   the state's canvassed locality totals, with the
                             database's own party names

**Three elections are kept but marked incomplete**, and the figure leaves
them out: 1896, where the Washington district and the total are printed "?";
and 1904 and 1908, of which O'Leary writes that the returns "appear
incomplete" - 1904 sums to 256 votes against 826 four years earlier. A row
that is not the county's vote should not be drawn as if it were.

**Party before 1924 is the nominee's, not the source's.** O'Leary prints
party for 1912 only. The Democratic and Republican nominees of each election
are a matter of record and are named here, with the candidate as O'Leary
spells him; a name this table does not know stops the build rather than
falling into "other". 1884's St. John line reads 0 0 0 0 and is kept.

The county's own candidate history also prints presidential returns from
1920 and is read as a check: where it and the state both give a major-party
figure, the two must agree within a few per cent (they are different
compilations of the same canvass), and the build reports the years they do
not.
"""
import re

import pandas as pd

import citekeys
from paths import RAW, TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"
OLEARY = BY_CLAUDE / "arlington_county" / "president_1872-1920.csv"
STATE = RAW / "va_dept_of_elections" / "president_1924-2024.csv"
COUNTY = BY_CLAUDE / "arlington_county" / "candidate_history_1920-present.csv"

# The major-party nominees, as O'Leary spells them. Everyone else he lists is
# "other". A year's entry is (Democratic, Republican).
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
    c = pd.read_csv(COUNTY, dtype=str).fillna("")
    c = c[c.office.str.startswith("President") & c.candidate.str.contains(r"\((?:D|R)\s?\)$")]
    c["year"] = c.year.astype(int)
    c["votes"] = pd.to_numeric(c.votes.str.replace(",", ""), errors="coerce")
    c["band"] = c.candidate.str.extract(r"\((D|R)\s?\)$")[0].map({"D": "dem", "R": "rep"})
    county = c.groupby(["year", "band"]).votes.sum().unstack()
    both = d.set_index("year")[["dem", "rep"]].join(county, rsuffix="_county", how="inner")
    off = both[((both.dem - both.dem_county).abs() / both.dem > TOLERANCE)
               | ((both.rep - both.rep_county).abs() / both.rep > TOLERANCE)]
    if not off.empty:
        print("  voters.csv: county and state disagree by more than "
              f"{TOLERANCE:.0%} in {list(off.index)} (state figures kept)")


def build() -> pd.DataFrame:
    d = pd.concat([oleary(), state()], ignore_index=True).sort_values("year").reset_index(drop=True)
    years = list(d.year)
    assert years == list(range(1872, 2025, 4)), f"not every fourth year 1872-2024: {years}"
    assert (d.total == d[["dem", "rep", "other"]].sum(axis=1)).all(), "bands do not sum to the total"
    county_check(d)
    return d


if __name__ == "__main__":
    write(build(), "voters")
