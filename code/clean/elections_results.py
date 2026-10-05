"""Arlington's vote by party, for President and for the County Board -> data/clean/elections_results.csv

One row per election and office: votes for Democratic, Republican, ABC and
other candidates, votes for candidates the source gives no label, the total,
and a source per row. `office` is "president" (every fourth year from 1872)
or "county board" (every year from 1931).

A County Board candidate is counted under the label the county's record
prints after their name, not under the party members.csv attaches to
the winner. A year whose returns are not the county's whole vote is marked
incomplete, on the rule in elections.contest_rows(). docs/elections.md has
the reasoning.

Three sources for the presidential vote, and a year takes the first that has it:

  the Commonwealth's return   1872, 1876-1916, 1924, 1928   the county's own
                             certified return for 1872, the Almanack's official
                             vote to 1916 and the Secretary's report from 1924,
                             keyed in elections_results_state.csv; a ticket is
                             Democratic, Republican or other by its printed party
  oleary2010     1920        the county's returns as O'Leary compiled them,
                             for the one year no state return was found;
                             party is the nominee's, named in NOMINEES
  vaelections    1932-2024   the state's canvassed locality totals

A year with a state return never takes O'Leary's (OLEARY_ONLY names the one
that does), and build() refuses a year in neither. The county's own
presidential returns are read as a check on the state's, and the build
reports the years they differ by more than TOLERANCE.

For 1892 and 1900, gazette_vs_almanack.apply() then replaces the
Commonwealth return's dem and rep with the Alexandria Gazette's own district
sum, which ties to O'Leary's figure independent of him; docs/elections.md,
"The Gazette's own district returns settle four of the nine," and
docs/questions.csv, gazette-vs-almanack-1892-1900.
"""
import re

import pandas as pd

import members_terms
import citekeys
import elections
import gazette_vs_almanack
import paths
from elections import COUNTY_HISTORY_THROUGH
from paths import write

# The major-party nominees, (Democratic, Republican), as O'Leary spells them.
NOMINEES = {
    1872: ("Greeley", "Grant"), 1876: ("Tilden", "Hayes"), 1880: ("Hancock", "Garfield"),
    1884: ("Cleveland", "Blaine"), 1888: ("Cleveland", "Harrison"), 1892: ("Cleveland", "Harrison"),
    1896: ("Bryan", "McKinley"), 1900: ("Bryan", "McKinley"), 1904: ("Parker", "Roosevelt"),
    1908: ("Bryan", "Taft"), 1912: ("Wilson", "Taft"), 1916: ("Wilson", "Hughes"),
    1920: ("Cox", "Harding"),
}
# The presidential years with no state return found (docs/elections.md, "The
# state's return, read against O'Leary's"), which take O'Leary's.
OLEARY_ONLY = {1920: "O'Leary's count; no state return found"}
LINE = re.compile(r"^(?P<name>[A-Za-z.'’ /]+?)(?:\s*\([^)]*\))?\s+(?P<counts>[\d,? ]+)$")
TOLERANCE = 0.05
BANDS = ["dem", "rep", "abc", "other", "unrecorded"]
# What the county's labels record (elections.LABELS) and the band each
# vote counts in.
BAND = {"Democratic": "dem", "Republican": "rep", "ABC": "abc",
        "independent": "other", "other": "other", "": "unrecorded"}

# The words data/transcribed/by_claude/candidates_party.csv carries for a
# non-Democratic County Board candidate since 2023, the state record's first
# year with no party on a candidate who did not win a Democratic primary; a
# word not listed here stops the build. docs/elections.md, voters-2023-labels.
CANDIDATE_PARTY_WORDS = {
    "independent": "independent",
    "independent; running under the banner of the forward party": "independent",
    "republican": "Republican",
    "republican for arlington county board": "Republican",
}


def oleary() -> pd.DataFrame:
    """O'Leary's presidential totals for the years in OLEARY_ONLY."""
    d = elections.oleary(elections.PRESIDENT)
    rows = []
    for year, g in d[d.year.isin(OLEARY_ONLY)].groupby("year"):
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
            else:
                votes["other"] += total
        if votes["dem"] == 0 and votes["rep"] == 0:
            raise ValueError(f"{year}: no line matched either nominee {NOMINEES[int(year)]}")
        rows.append({"year": int(year), **votes,
                     "total": sum(votes.values()),
                     "complete": True,
                     "source": f"{citekeys.OLEARY} p.{g.page.iloc[0]}",
                     "note": OLEARY_ONLY[int(year)]})
    return pd.DataFrame(rows)


def state_return() -> pd.DataFrame:
    """The Commonwealth's return, its tickets summed into the three bands: a
    Democratic ticket (Hancock's Funder and Readjuster electors are one) is
    dem, a Republican one rep, any other other. Where the Almanack prints
    only the highest candidates, other is what it prints. A dotted ticket
    was keyed as 0. A year's source is its citekey; every ticket in a year
    shares one. gazette_vs_almanack.apply() then replaces YEARS with the
    Gazette's own district return."""
    r = elections.state_return()
    r["band"] = r.party.map({"Democratic": "dem", "Republican": "rep"}).fillna("other")
    g = r.pivot_table(index="year", columns="band", values="votes", aggfunc="sum",
                      fill_value=0).reset_index()
    sources = r.groupby("year").source.agg(lambda v: "; ".join(sorted(set(v))))
    g["total"] = g[["dem", "rep", "other"]].sum(axis=1)
    g["complete"] = True
    g["source"] = g.year.map(sources)
    g["note"] = ""
    g = gazette_vs_almanack.apply(g)
    return g[["year", "dem", "rep", "other", "total", "complete", "source", "note"]]


def state() -> pd.DataFrame:
    s = elections.contests(elections.PRESIDENT)
    s = s[(s.record == "state") & s.person].copy()
    s["votes"] = s.votes.astype(int)
    s["band"] = s.party.map({"Democratic": "dem", "Republican": "rep"}).fillna("other")
    g = s.pivot_table(index=["year", "contest"], columns="band", values="votes", aggfunc="sum",
                      fill_value=0).reset_index()
    g["total"] = g[["dem", "rep", "other"]].sum(axis=1)
    g["complete"] = True
    g["source"] = [f"{citekeys.VA_ELECTIONS} contest {c}" for c in g.contest]
    g["note"] = ""
    return g[["year", "dem", "rep", "other", "total", "complete", "source", "note"]]


def presidential() -> pd.DataFrame:
    """One row per presidential year: the state's return where one is keyed,
    O'Leary's for OLEARY_ONLY, and the state database's from the first year
    neither covers. A year in both the return and the database must agree on
    the two parties; the return's other votes may exceed the database's,
    which leaves a minor ticket out of its locality rows (1928), and the
    year's note says so."""
    ret, olearys, database = state_return(), oleary(), state()
    both = set(ret.year) & set(olearys.year)
    if both:
        raise ValueError(f"{sorted(both)}: a year with a state return keyed takes nothing "
                         f"from O'Leary; remove it from OLEARY_ONLY")
    covered = set(ret.year) | set(olearys.year)
    uncovered = {y for y in range(1872, int(database.year.min()) + 1, 4)} - covered
    if uncovered:
        raise ValueError(f"{sorted(uncovered)}: no state return keyed and not in OLEARY_ONLY, "
                         f"so no presidential count; key the state's return or name the year")
    db = database.set_index("year")
    for i, r in ret.iterrows():
        if r.year not in db.index:
            continue
        d = db.loc[r.year]
        if (r.dem, r.rep) != (d.dem, d.rep) or r.other < d.other:
            raise ValueError(f"{r.year}: the Commonwealth's return ({r.dem}, {r.rep}, {r.other}) "
                             f"and the state database ({d.dem}, {d.rep}, {d.other}) disagree "
                             f"on more than minor tickets")
        if r.other > d.other:
            ret.loc[i, "note"] = (f"the Secretary's return prints {r.other - d.other} votes for minor "
                                  f"tickets that the state database's locality rows leave out")
    return pd.concat([ret, olearys, database[~database.year.isin(ret.year)]],
                     ignore_index=True)


def county_check(d: pd.DataFrame):
    """The county's own presidential returns, against the state's."""
    c = elections.county_history(elections.PRESIDENT)
    c = c[c.candidate.str.contains(r"\((?:D|R)\s?\)$")].copy()
    c["band"] = c.candidate.str.extract(r"\((D|R)\s?\)$")[0].map({"D": "dem", "R": "rep"})
    county = c.groupby(["year", "band"]).votes.sum().unstack()
    both = d.set_index("year")[["dem", "rep"]].join(county, rsuffix="_county", how="inner")
    off = both[((both.dem - both.dem_county).abs() / both.dem > TOLERANCE)
               | ((both.rep - both.rep_county).abs() / both.rep > TOLERANCE)]
    if not off.empty:
        print("  elections_results.csv: county and state disagree by more than "
              f"{TOLERANCE:.0%} in {list(off.index)} (state figures kept)")


def candidate_parties() -> dict:
    """(year, surname) -> (band, source, note) for a County Board
    general-election candidate the state record carries no party for, from
    data/built/candidates_party.csv: the party a press or campaign source gives,
    decoded through CANDIDATE_PARTY_WORDS."""
    a = paths.built("candidates_party")
    out = {}
    for _, r in a.iterrows():
        word = r.party_words.strip().lower()
        if word not in CANDIDATE_PARTY_WORDS:
            raise ValueError(f"{r['name']} {r.year}: party words with no category here: "
                             f"{r.party_words!r}; add them to CANDIDATE_PARTY_WORDS in "
                             f"elections_results.py or fix the reading")
        key = (int(r.year), elections.surname(r["name"]))
        out[key] = (BAND[CANDIDATE_PARTY_WORDS[word]], r.source,
                    f"{r.basis}: {r.quote}" if r.quote else r.basis)
    return out


def county_board() -> pd.DataFrame:
    """1931 on: every general and special County Board contest in a year,
    summed; primaries and write-ins left out. A county candidate is counted
    under the label the county prints. A state candidate is counted under
    the state's party, or as Democratic if they won that year's Democratic
    primary; since 2023, when the state record stopped naming a
    non-Democratic candidate's party, a press or campaign source stands in
    (candidate_parties()); failing both, unrecorded."""
    c = elections.contests()
    c = c[(c.record == "county") | (c.year > COUNTY_HISTORY_THROUGH)]
    won_primary = c[c.primary & c.person & (c.primary_party == "Democratic") & (c.is_winner == True)]  # noqa: E712
    dem_primary = set(zip(won_primary.year, won_primary.surname))
    attributed = candidate_parties()
    rows = []
    for year, g in c[~c.primary].groupby("year"):
        counts = dict.fromkeys(BANDS, 0)
        if g.record.iloc[0] == "county":
            named, complete, note = elections.contest_rows(g)
            for _, r in named[named.person & named.votes.notna()].iterrows():
                label = elections.label_of(r.candidate, where=f"{year}: ")
                counts[BAND[elections.LABELS[label]] if label else "unrecorded"] += int(r.votes)
            source = named.source.iloc[0]
        else:
            g = g[g.person]
            extra_sources, extra_notes = [], []
            for _, r in g.iterrows():
                attribution = attributed.get((year, r.surname))
                if r.party == "Democratic" or (year, r.surname) in dem_primary:
                    band = "dem"
                elif r.party == "Republican":
                    band = "rep"
                elif isinstance(r.party, str):
                    band = "other"
                elif attribution:
                    band, cite, note_ = attribution
                    if cite not in extra_sources:
                        extra_sources.append(cite)
                    extra_notes.append(note_)
                else:
                    band = "unrecorded"
                counts[band] += int(r.votes)
            complete = True
            note = ("party from the Democratic primary; the general carries none"
                    if g.party.isna().all() else "")
            source = (f"{citekeys.VA_ELECTIONS} contest "
                      + ", ".join(sorted(g.contest.unique(), key=int)))
            if extra_sources:
                source += "; " + "; ".join(extra_sources)
            if extra_notes:
                note = "; ".join(filter(None, [note, "; ".join(extra_notes)]))
        rows.append({"year": int(year), "office": "county board", **counts,
                     "total": sum(counts.values()), "complete": complete,
                     "source": source, "note": note})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    pres = presidential()
    pres["office"] = "president"
    pres["abc"] = 0
    pres["unrecorded"] = 0
    years = sorted(pres.year)
    assert years == list(range(1872, 2025, 4)), f"not every fourth year 1872-2024: {years}"
    county_check(pres)
    board = county_board()
    years = sorted(board.year)
    # Four-year terms for the whole Board in 1931 and 1935; one seat a year from 1939.
    assert years == [1931, 1935] + list(range(1939, members_terms.PRESENT)), \
        f"County Board elections are not 1931, 1935, then every year to {members_terms.PRESENT - 1}: {years}"
    d = pd.concat([pres, board], ignore_index=True)
    cols = ["year", "office", *BANDS, "total", "complete", "source", "note"]
    d = d[cols].sort_values(["office", "year"], ascending=[False, True]).reset_index(drop=True)
    assert (d.total == d[BANDS].sum(axis=1)).all(), "bands do not sum to the total"
    return d


if __name__ == "__main__":
    write(build(), "elections_results")
