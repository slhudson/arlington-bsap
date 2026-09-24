"""Who votes for the County Board, year by year -> data/clean/turnout.csv

One row per year in which any of four things is measured, 1872-2025:

  board_votes      every vote cast in the November County Board contests,
                   write-ins included, and how many seats they filled
  board_voters     the people that represents - see below
  registered       Arlington's registered voters at that November's election
  voting_age       the county's population 18 and over, in a census year, and
                   voting_age_est the same carried between censuses
  president_votes  the county's presidential vote, every fourth year
  cycle            what else the November ballot carried, from 1931: the
                   President, the governor, Congress alone, or the House of
                   Delegates alone - the year's place in the four-year cycle

Each measure has its own `_source` column, as residents.csv does, because a
row draws on up to four documents at once.

**Votes are not voters.** A County Board ballot carries one vote per seat
being filled, so in a two-seat year the contest's total is up to twice the
number of people who voted in it. `board_voters` divides the votes by the
seats: exactly the number of people who voted for the Board when one seat
was filled, and a lower bound when more than one was - a voter who marked
only one of two choices is counted as half. The seats are counted from the
roster (board_members.csv): the terms that began the following January, or
in November for a special election held the same day, appointments excluded.
That is what makes 1931, 1935 and 1939 five-seat elections (the whole Board
was elected at once until terms were staggered), and 1943, 1947, 1952 and
1997 more than the contest's own heading says.

Before 1932 the Board was elected by district, one seat each, so every voter
cast one vote and the county's total is the number who voted. O'Leary
reports the count for two of those elections, 1907 and 1915, and "(No
returns.)" for the rest; the two are here, with `board_seats` 3.

**Which years are not the county's vote.** The county's own candidate
history says its tallies are complete only from 1971. A year is marked
incomplete, and the figure leaves it out, where a named candidate has no
count (1942, 1949, and Frisbie in 1947, whose page also says its totals
are from 8 of 11 precincts) or where the page says others ran who are not
listed (1931). The note column says which.

**Registration is the state's active list**, from 2010, when its monthly
reports begin; `registered_all` adds the inactive list. Nothing before 2010
is online, so turnout as a share of the registered is a fifteen-year series.
Voting-age population is the census's population 18 and over, from 1980,
when it can be read from the archived Summary Tape Files; `voting_age_est`
carries it into every year between censuses, on a straight line, for the
figure's share panel. Earlier censuses printed the count of those 21 and
over, and the 1971 change of the voting age would have to be handled; that
is left open in Q31 of docs/questions.md.

**The presidential vote is voters.csv's**, the county's total for the office
in each presidential year, so the two figures agree by construction; its
source column says so.

Three guards, the first two tested in code/tests.py: the Board's voters can
never exceed the registered voters, nor the presidential vote of the same
year, and the registered can never exceed the adults. Any of them would mean
a total had been read as a per-candidate figure, or votes counted twice, or
a state total read as the county's, and the figure would draw it without
complaint.
"""
import re

import pandas as pd

import board_roster
import citekeys
from paths import CLEAN, RAW, TRANSCRIBED, write

COUNTY = TRANSCRIBED / "by_claude" / "arlington_county" / "candidate_history_1920-present.csv"
OLEARY = TRANSCRIBED / "by_claude" / "arlington_county" / "board_1870-1920.csv"
STATE = RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"
REGISTRATION = RAW / "va_dept_of_elections" / "registration_2010-2025.csv"
CENSUS = RAW / "us_census_bureau"
ROSTER = CLEAN / "board_members.csv"
VOTERS = CLEAN / "voters.csv"

COUNTY_THROUGH = 2021          # the county's candidate history ends here
# The population 18 and over, census by census. From 2000 the Bureau
# publishes it as a table whose first cell is the total; 1980 and 1990 come
# from the age distribution, summed from the "18" cell to the end. Each
# entry is (file under data/raw/us_census_bureau/, the columns to sum).
VOTING_AGE = {
    1980: ("1980/stf1a_table10_age_virginia_counties.csv", "from 18"),
    1990: ("1990/stf1a_age_virginia_counties.csv", "from 18"),
    2000: ("2000/censusapi_dec_sf1_P005_race_18_and_over_virginia_counties.csv", ["P005001"]),
    2010: ("2010/censusapi_dec_sf1_P10_race_18_and_over_virginia_counties.csv", ["P010001"]),
    2020: ("2020/censusapi_dec_pl_P3_race_18_and_over_virginia_counties.csv", ["P3_001N"]),
}
VOTING_AGE_SOURCE = {1980: citekeys.CENSUS_1980_STF1A, 1990: citekeys.CENSUS_1990_STF1A}
# What else is on Arlington's November ballot, by the year's place in the
# four-year cycle. Virginia has elected its governor in the year after a
# presidential election since 1869 and its House of Delegates in every odd
# year, and Congress is on the ballot in even years; so the four Novembers
# are, in order: President, the governor, Congress alone (the midterm), and
# the House of Delegates alone. The Board is the top of the ballot only in
# the last of these.
CYCLE = {0: "president", 1: "governor", 2: "midterm", 3: "delegates"}
# A County Board contest's heading, whatever qualifier follows it.
BOARD = re.compile(r"^(Member, )?County Board\b")
# What the county prints when a year's total is not the county's vote.
PARTIAL = re.compile(r"not mentioned|not final|\d+ of \d+ precincts", re.I)
# A row that names a candidate, as against prose about the contest.
CANDIDATE = re.compile(r"^[*A-Z]")


def seats_filled(roster: pd.DataFrame, year: int) -> int:
    """Seats the November election of `year` filled: terms an election
    seated the next January, or a special election seated that November.
    An appointment is not an election, and a special election in another
    month (January 1996) filled its seat then. The roster's seated_by says
    which each term is."""
    regular = ((roster.seated_by == board_roster.ELECTION)
               & (roster.start_year == year + 1) & (roster.start_month == 1))
    special = ((roster.seated_by == board_roster.SPECIAL_ELECTION)
               & (roster.start_year == year) & (roster.start_month == 11))
    n = int((regular | special).sum())
    if not 1 <= n <= 5:
        raise AssertionError(f"{year}: the roster has {n} terms beginning after the "
                             f"November election; a Board of five cannot fill that many")
    return n


def board_county(roster) -> pd.DataFrame:
    """1931-2021: every November County Board contest the county lists."""
    c = pd.read_csv(COUNTY, dtype=str).fillna("")
    c = c[c.office.str.match(BOARD) & ~c.office.str.contains("Candidates")
          & c.year.str.match(r"^\d{4}$") & c.election_date.str.startswith("November")
          & ~c.election_kind.str.contains("Primary")].copy()
    c["year"] = c.year.astype(int)
    c["votes"] = pd.to_numeric(c.votes.str.replace(",", ""), errors="coerce")
    rows = []
    for year, g in c.groupby("year"):
        # 1935 and 1939 print the new Board's composition, without counts,
        # beside the returns. A block (one page, one date) with no count on
        # any row is that list, not a contest, unless the year has no counts
        # anywhere - then it is the contest, and the year is incomplete.
        blocks = g.groupby(["page", "election_date"]).votes.apply(lambda v: v.notna().any())
        if blocks.any():
            g = g[[blocks[k] for k in zip(g.page, g.election_date)]]
        named = g[g.candidate.str.match(CANDIDATE) & ~g.candidate.str.contains(":")].copy()
        # 1947 prints the same block twice, on facing pages; a candidate with
        # the same count twice in one year is one candidate.
        named["key"] = [board_roster.surname(n.lstrip("*W. ")) for n in named.candidate]
        named = named.drop_duplicates(["key", "votes"])
        missing = sorted(named[named.votes.isna()].key.unique())
        partial = [t for t in pd.concat([g.candidate, g.office]) if PARTIAL.search(t)]
        note = "; ".join(filter(None, [
            f"no vote count for {', '.join(missing)}" if missing else "",
            partial[0] if partial else ""]))
        rows.append({"year": year, "board_votes": int(named.votes.sum()),
                     "board_seats": seats_filled(roster, year),
                     "board_complete": not (missing or partial),
                     "board_source": f"{citekeys.ARLINGTON_ELECTIONS} p.{g.page.iloc[0]}",
                     "board_note": note})
    return pd.DataFrame(rows)


def board_state() -> pd.DataFrame:
    """2022 on: the state's November general contests, all votes cast."""
    s = pd.read_csv(STATE, low_memory=False)
    s["date"] = pd.to_datetime(s.election_date)
    s = s[s.election_type.str.startswith("General") & (s.date.dt.month == 11)
          & (s.date.dt.year > COUNTY_THROUGH)]
    votes = s[~s.candidate_name.str.match(r"^(Total|Under|Over)")]
    rows = []
    for year, g in votes.groupby(votes.date.dt.year):
        rows.append({"year": int(year), "board_votes": int(g.votes.sum()),
                     "board_seats": int(g.groupby("contest_id").number_seats.first().sum()),
                     "board_complete": True,
                     "board_source": f"{citekeys.VA_ELECTIONS} contest "
                                     + ", ".join(str(c) for c in sorted(g.contest_id.unique())),
                     "board_note": ""})
    return pd.DataFrame(rows)


def board_districts() -> pd.DataFrame:
    """1870-1915: the elections for which O'Leary reports a count in every
    district. An entry reads "Corbett 213 Hagen 189"; one without counts
    reads "(No returns.)" or a name alone, and the year is left out."""
    d = pd.read_csv(OLEARY)
    rows = []
    for year, g in d.groupby("year"):
        counts = [re.findall(r"(\d[\d,]*)(?=\s|$)", e) for e in g.entry]
        if not all(counts) or len(g) != 3:
            continue
        total = sum(int(n.replace(",", "")) for c in counts for n in c)
        rows.append({"year": int(year), "board_votes": total, "board_seats": 3,
                     "board_complete": True,
                     "board_source": f"{citekeys.OLEARY} p.{g.page.iloc[0]}",
                     "board_note": "one seat per district, so one vote per voter"})
    if not rows:
        raise AssertionError("no district election with a count in every district - "
                             "1907 and 1915 should be there")
    return pd.DataFrame(rows)


def registration() -> pd.DataFrame:
    r = pd.read_csv(REGISTRATION)
    return pd.DataFrame({
        "year": r.year, "registered": r.active, "registered_all": r["all"],
        "registered_source": [f"{citekeys.VA_REGISTRATION} {rep}" + (f", as of {d}" if isinstance(d, str) else "")
                              for rep, d in zip(r.report, r.as_of)]})


def voting_age() -> pd.DataFrame:
    rows = []
    for year, (file, cols) in VOTING_AGE.items():
        t = pd.read_csv(CENSUS / file)
        name = "NAME" if "NAME" in t.columns else "name"
        arl = t[t[name].str.upper().str.startswith("ARLINGTON")]   # the STF names are upper case
        assert len(arl) == 1, f"{file}: {len(arl)} Arlington rows"
        if cols == "from 18":
            ages = list(t.columns[3:])
            cols = ages[ages.index("18"):]
            assert ages[0] == "under_1" and cols[-1] == "85_over", ages
        rows.append({"year": year, "voting_age": int(arl[cols].iloc[0].sum()),
                     "voting_age_source": f"{VOTING_AGE_SOURCE.get(year, citekeys.CENSUS_DATA_FILE)} "
                                          f"{file.split('/')[1]}"})
    return pd.DataFrame(rows)


def between_censuses(d: pd.DataFrame) -> pd.Series:
    """The voting-age population in every year from the first census that
    reports it: the census count in a census year, a straight line between
    two censuses, and the last census's count carried forward after it.

    A denominator for the share panel and nothing else. Linear is the
    plainest assumption and is stated here rather than in a figure script,
    because it makes a number; carrying 2020 forward understates the county's
    growth since, so the shares after 2020 are, if anything, high.
    """
    known = d.dropna(subset=["voting_age"]).set_index("year").voting_age
    est = pd.Series(index=d.year.to_numpy(), dtype=float)
    est.loc[known.index] = known.to_numpy(dtype=float)
    est = est.interpolate(method="index").ffill()
    est[est.index < known.index.min()] = float("nan")
    return est.to_numpy()


def president() -> pd.DataFrame:
    v = pd.read_csv(VOTERS)
    if "office" in v.columns:
        v = v[v.office == "president"]
    v = v[v.complete]
    return pd.DataFrame({"year": v.year, "president_votes": v.total,
                         "president_source": citekeys.DERIVED})


def build() -> pd.DataFrame:
    roster = pd.read_csv(ROSTER)
    board = pd.concat([board_districts(), board_county(roster), board_state()], ignore_index=True)
    # The whole Board was elected every fourth year until terms were
    # staggered from 1940; from then on a seat is filled every November.
    years = list(board[board.year >= 1931].year)
    assert years == [1931, 1935, 1939] + list(range(1940, 2026)), \
        f"a November Board contest is missing or extra: {years}"
    board["board_voters"] = (board.board_votes / board.board_seats).round().astype(int)

    d = board
    for part in (registration(), voting_age(), president()):
        d = d.merge(part, on="year", how="outer")
    d = d.sort_values("year").reset_index(drop=True)
    d["cycle"] = [CYCLE[y % 4] if y >= 1931 else "" for y in d.year]
    d["voting_age_est"] = between_censuses(d)
    d["voting_age_est_source"] = [citekeys.DERIVED if pd.notna(v) else "" for v in d.voting_age_est]

    # The guards. Both compare people with people, so an undercount from the
    # per-seat division only makes them easier to pass, never harder.
    both = d.dropna(subset=["board_voters", "registered"])
    over = both[both.board_voters > both.registered]
    assert over.empty, f"more Board voters than registered voters in {list(over.year)}"
    both = d.dropna(subset=["board_voters", "president_votes"])
    over = both[both.board_voters > both.president_votes]
    assert over.empty, f"more Board voters than presidential voters in {list(over.year)}"

    both = d.dropna(subset=["registered", "voting_age_est"])
    over = both[both.registered > both.voting_age_est]
    assert over.empty, f"more registered voters than adults in {list(over.year)}"

    for c in ("board_votes", "board_seats", "board_voters", "registered", "registered_all",
              "voting_age", "voting_age_est", "president_votes"):
        d[c] = d[c].round().astype("Int64")
    for c in ("board_source", "board_note", "registered_source", "voting_age_source", "president_source"):
        d[c] = d[c].fillna("")           # a year the measure does not cover cites nothing
    cols = ["year", "cycle", "board_votes", "board_seats", "board_voters", "board_complete", "board_source",
            "board_note", "registered", "registered_all", "registered_source",
            "voting_age", "voting_age_source", "voting_age_est", "voting_age_est_source",
            "president_votes", "president_source"]
    return d[cols]


if __name__ == "__main__":
    write(build(), "turnout")
