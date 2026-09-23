"""Arlington's vote by party, for President and for the County Board -> data/clean/voters.csv

One row per election and office: votes for Democratic, Republican, ABC and
other candidates, votes for candidates the source gives no label, the total,
and a source per row. `office` is "president" (every fourth year from 1872)
or "county board" (every year from 1931).

**The two are not the same electorate and are not coded the same way.** The
presidential vote is the county's partisanship as the whole electorate
expresses it; the County Board vote is what the smaller November electorate
did with the candidates it was offered. A Board candidate is counted under
the label the county's own record prints after their name - "(D)", "(ABC)",
"(I)" - and not under the party reporting later attached to the winners in
board_members.csv. Votes for Dorothy Grotos in 1975 sit in "other" here and
her seat sits in Republican there, deliberately: this file is about the
choice voters were offered, that one about who sat. Candidates the county
prints no label for are "unrecorded", and a year in which a named candidate
has no vote count is marked incomplete and not drawn.

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
import difflib
import re

import pandas as pd

import citekeys
from paths import CLEAN, RAW, TRANSCRIBED, write

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


# The county's labels, as printed after a candidate's name, and the band each
# counts in. The set here is every label a County Board candidate has carried
# in the transcription; a new one stops the build.
BOARD_LABELS = {
    "D": "dem", "R": "rep", "ABC": "abc",
    "I": "other", "IM": "other", "AIM": "other", "NP": "other", "Non-Part.": "other",
    "Non-Partisan": "other", "Ind. Dem.": "other", "Ind. Rep.": "other", "G": "other",
    "IG": "other", "Va. Reform": "other",
    "Rep.": "rep",
    "Convention": "unrecorded",       # nominated by a convention the source does not name
}
NOT_A_LABEL = {"won", "inc.", "holdover", "not on ballot"}
LABEL = re.compile(r"\(([^()]*)\)")
BOARD_STATE_FROM = 2022             # the county's history ends at 2021, as in board_roster
BOARD_FILE = RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"


def county_board_county() -> pd.DataFrame:
    """1931-2021 from the county's candidate history: every general and
    special County Board contest in a year, summed; primaries left out."""
    c = pd.read_csv(COUNTY, dtype=str).fillna("")
    c = c[c.office.str.contains("County Board") & ~c.office.str.contains("Candidates")
          & c.year.str.match(r"^\d{4}$") & ~c.election_kind.str.contains("Primary")]
    # A candidate row names a person. Prose rows - "(others not mentioned)",
    # "[Listing attached]", "Running Before Primary:" - and write-ins are not.
    c = c[c.candidate.str.match(r"^[*A-Za-z]") & ~c.candidate.str.contains(":")
          & ~c.candidate.str.contains("write", case=False)].copy()
    c["votes"] = pd.to_numeric(c.votes.str.replace(",", ""), errors="coerce")
    winners = elected_winners()
    rows = []
    for year, g in c.groupby(c.year.astype(int)):
        counts = {"dem": 0, "rep": 0, "abc": 0, "other": 0, "unrecorded": 0}
        for _, r in g.iterrows():
            if pd.isna(r.votes):
                continue
            labels = {l.strip() for l in LABEL.findall(r.candidate)} - NOT_A_LABEL
            if len(labels) > 1:
                raise ValueError(f"{year}: {r.candidate!r} carries more than one label")
            label = next(iter(labels), "")
            if label and label not in BOARD_LABELS:
                raise ValueError(f"{year}: label ({label}) on {r.candidate!r} is not one this "
                                 "build knows - add it to BOARD_LABELS")
            counts[BOARD_LABELS[label] if label else "unrecorded"] += int(r.votes)
        # A winner with no vote count means the year's returns are not the
        # county's vote: Campbell unopposed in 1942, DeLashmutt "re-elected"
        # in 1941, nobody counted in 1949. Losers without counts - the 1939
        # primary field, the 1935 composition list - do not make a year
        # incomplete. Winners come from the roster: the members whose term
        # begins the following January by election.
        # The county spells a few winners differently from Novack - Kelly for
        # Kelley, Mcgruder for Magruder, Blevens for Blevins - so a surname
        # counts as present when a close spelling has a vote count.
        counted = set(g[g.votes.notna()].candidate.map(_surname))
        missing = sorted(w for w in winners.get(int(year), set())
                         if not difflib.get_close_matches(w, counted, n=1, cutoff=0.8))
        rows.append({"year": int(year), "office": "county board", **counts,
                     "total": sum(counts.values()), "complete": not missing,
                     "source": f"{citekeys.ARLINGTON_ELECTIONS} p.{g.page.iloc[0]}",
                     "note": f"no vote count for {', '.join(missing)}" if missing else ""})
    return pd.DataFrame(rows)


def _surname(candidate):
    import board_roster
    return board_roster.surname(candidate)


def elected_winners() -> dict:
    """Election year -> surnames of the members it seated in January.

    Read from data/clean/board_members.csv, which the build writes first
    (run.sh orders it so), the way board_seats.py reads it. An appointee's
    term begins mid-year and is not an election result.
    """
    m = pd.read_csv(CLEAN / "board_members.csv")
    m["note"] = m.note.fillna("")
    # The term before this one, for the same person, if it ended the
    # previous December: a January term that continues an appointment is
    # Novack's span split at an election the person stood in but did not
    # win (Frisbie, 1947), not a win.
    prev = m.set_index(["name", "term_number"])
    def continues_appointment(t):
        if t.term_number == 1:
            return False
        p = prev.loc[(t["name"], t.term_number - 1)]
        return (p.end_year == t.start_year - 1 and p.end_month == 12
                and p.note.startswith("Appointed"))
    out = {}
    for _, t in m.iterrows():
        if (t.start_year < 1932 or t.start_month != 1 or t.note.startswith("Appointed")
                or t.note.startswith("Elected in a special election") or continues_appointment(t)):
            continue
        out.setdefault(int(t.start_year) - 1, set()).add(_surname(t["name"]))
    return out


def county_board_state() -> pd.DataFrame:
    """2022 on from the state database. Its general-election rows carry a
    party through 2022 and none after; a candidate who won that year's
    Democratic primary is counted Democratic, and the rest are unrecorded."""
    s = pd.read_csv(BOARD_FILE, low_memory=False)
    s = s[~s.candidate_name.str.match(r"^(Total|Write|Under|Over)", na=False)].copy()
    s["year"] = pd.to_datetime(s.election_date).dt.year
    s = s[s.year >= BOARD_STATE_FROM]
    dem_primary = set(zip(s[s.election_type.str.startswith("Primary") & (s.primary_party == "Democratic")
                             & s.is_winner].year,
                          s[s.election_type.str.startswith("Primary") & (s.primary_party == "Democratic")
                            & s.is_winner].candidate_name.map(_surname)))
    general = s[s.election_type.str.startswith("General")].copy()
    general["band"] = [
        "dem" if p == "Democratic" or (y, _surname(n)) in dem_primary
        else "rep" if p == "Republican" else "other" if isinstance(p, str) else "unrecorded"
        for p, y, n in zip(general.candidate_party_name, general.year, general.candidate_name)]
    rows = []
    for year, g in general.groupby("year"):
        counts = g.groupby("band").votes.sum().reindex(["dem", "rep", "abc", "other", "unrecorded"], fill_value=0)
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
    cols = ["year", "office", "dem", "rep", "abc", "other", "unrecorded", "total", "complete", "source", "note"]
    d = d[cols].sort_values(["office", "year"], ascending=[False, True]).reset_index(drop=True)
    assert (d.total == d[["dem", "rep", "abc", "other", "unrecorded"]].sum(axis=1)).all(), "bands do not sum to the total"
    return d


if __name__ == "__main__":
    write(build(), "voters")
