"""Who votes for the County Board, year by year -> data/clean/turnout.csv

One row per year in which any of these is measured, 1872-2025:

  board_votes      every vote cast in the November County Board contests,
                   write-ins included, and board_seats, how many seats
                   they filled
  board_voters     votes divided by seats: the people that represents,
                   exactly for one seat and a lower bound for two or more
  registered       Arlington's active registered voters at that November's
                   election, from 2010; registered_all adds the inactive
  voting_age       the population 18 and over in a census year, from 1980,
                   and voting_age_est the same carried between censuses
  president_votes  the county's presidential vote, from voters.csv
  cycle            what else the November ballot carried, from 1931

Each measure has its own `_source` column. The seats an election filled
are counted from the roster: terms an election seated the next January, or
a special election that November. A year is marked incomplete on the rule
in elections.contest_rows(). docs/voters.md has the reasoning.

Three guards: the Board's voters never exceed the registered voters, nor
the presidential vote of the same year, and the registered never exceed
the adults.
"""
import re

import pandas as pd

import board_roster
import census
import citekeys
import elections
import paths
from elections import COUNTY_HISTORY_THROUGH
from paths import read, write

# The population 18 and over: from 2000 a table whose first cell is the
# total; 1980 and 1990 the age distribution summed from the "18" cell on.
VOTING_AGE = {
    1980: ("1980/stf1a_table10_age_virginia_counties.csv", "from 18"),
    1990: ("1990/stf1a_age_virginia_counties.csv", "from 18"),
    2000: ("2000/censusapi_dec_sf1_P005_race_18_and_over_virginia_counties.csv", ["P005001"]),
    2010: ("2010/censusapi_dec_sf1_P10_race_18_and_over_virginia_counties.csv", ["P010001"]),
    2020: ("2020/censusapi_dec_pl_P3_race_18_and_over_virginia_counties.csv", ["P3_001N"]),
}
VOTING_AGE_SOURCE = {1980: citekeys.CENSUS_1980_STF1A, 1990: citekeys.CENSUS_1990_STF1A}
# The year's place in Virginia's four-year cycle, by year mod 4.
CYCLE = {0: "president", 1: "governor", 2: "midterm", 3: "delegates"}


def seats_filled(roster: pd.DataFrame, year: int) -> int:
    """Seats the November election of `year` filled: terms an election
    seated the next January, or a special election seated that November."""
    regular = ((roster.seated_by == board_roster.ELECTION)
               & (roster.start_year == year + 1) & (roster.start_month == 1))
    special = ((roster.seated_by == board_roster.SPECIAL_ELECTION)
               & (roster.start_year == year) & (roster.start_month == 11))
    n = int((regular | special).sum())
    if not 1 <= n <= 5:
        raise AssertionError(f"{year}: the roster has {n} terms beginning after the "
                             f"November election; a Board of five cannot fill that many")
    return n


def board_votes(roster) -> pd.DataFrame:
    """1931 on: every November County Board contest, all votes cast,
    write-ins included. The county's years go through contest_rows(); the
    state's are complete, and count their seats from the contest."""
    c = elections.contests()
    c = c[c.november & ~c.primary
          & ((c.record == "county") | (c.year > COUNTY_HISTORY_THROUGH))]
    rows = []
    for year, g in c.groupby("year"):
        if g.record.iloc[0] == "county":
            named, complete, note = elections.contest_rows(g)
            votes, seats, source = named.votes.sum(), seats_filled(roster, year), named.source.iloc[0]
        else:
            g = g[g.person | g.writein]
            votes, complete, note = g.votes.sum(), True, ""
            seats = g.groupby("contest").seats.first().sum()
            source = (f"{citekeys.VA_ELECTIONS} contest "
                      + ", ".join(sorted(g.contest.unique(), key=int)))
        rows.append({"year": int(year), "board_votes": int(votes), "board_seats": int(seats),
                     "board_complete": complete, "board_source": source, "board_note": note})
    return pd.DataFrame(rows)


def board_districts() -> pd.DataFrame:
    """1870-1915: the elections for which O'Leary reports a count in every
    district."""
    d = elections.oleary(elections.SUPERVISORS)
    rows = []
    for year, g in d.groupby("year"):
        counts =[re.findall(r"(\d[\d,]*)(?=\s|$)", e) for e in g.entry]
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
    r = paths.typed(paths.built("registration"))
    return pd.DataFrame({
        "year": r.year, "registered": r.active, "registered_all": r["all"],
        "registered_source": [f"{citekeys.VA_REGISTRATION} {rep}" + (f", as of {d}" if isinstance(d, str) else "")
                              for rep, d in zip(r.report, r.as_of)]})


def voting_age() -> pd.DataFrame:
    rows = []
    for year, (file, cols) in VOTING_AGE.items():
        t = census.table("raw/us_census_bureau/" + file)
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
    reports it: a straight line between censuses, the last carried forward."""
    known = d.dropna(subset=["voting_age"]).set_index("year").voting_age
    est = pd.Series(index=d.year.to_numpy(), dtype=float)
    est.loc[known.index] = known.to_numpy(dtype=float)
    est = est.interpolate(method="index").ffill()
    est[est.index < known.index.min()] = float("nan")
    return est.to_numpy()


def president() -> pd.DataFrame:
    v = read("voters")
    v = v[(v.office == "president") & v.complete]
    return pd.DataFrame({"year": v.year, "president_votes": v.total,
                         "president_source": citekeys.DERIVED})


def build() -> pd.DataFrame:
    roster = read("board_members")
    board = pd.concat([board_districts(), board_votes(roster)], ignore_index=True)
    # The whole Board was elected every fourth year until terms were
    # staggered from 1940; from then on a seat is filled every November.
    years = list(board[board.year >= 1931].year)
    assert years == [1931, 1935, 1939] + list(range(1940, board_roster.PRESENT)), \
        f"a November Board contest is missing or extra: {years}"
    board["board_voters"] = (board.board_votes / board.board_seats).round().astype(int)

    d = board
    for part in (registration(), voting_age(), president()):
        d = d.merge(part, on="year", how="outer")
    d = d.sort_values("year").reset_index(drop=True)
    d["cycle"] = [CYCLE[y % 4] if y >= 1931 else "" for y in d.year]
    d["voting_age_est"] = between_censuses(d)
    d["voting_age_est_source"] = [citekeys.DERIVED if pd.notna(v) else "" for v in d.voting_age_est]

    for a, b, what in (("board_voters", "registered", "more Board voters than registered voters"),
                       ("board_voters", "president_votes", "more Board voters than presidential voters"),
                       ("registered", "voting_age_est", "more registered voters than adults")):
        both = d.dropna(subset=[a, b])
        over = both[both[a] > both[b]]
        assert over.empty, f"{what} in {list(over.year)}"

    for c in ("board_votes", "board_seats", "board_voters", "registered", "registered_all",
              "voting_age", "voting_age_est", "president_votes"):
        d[c] = d[c].round().astype("Int64")
    for c in ("board_source", "board_note", "registered_source", "voting_age_source", "president_source"):
        d[c] = d[c].fillna("")
    cols = ["year", "cycle", "board_votes", "board_seats", "board_voters", "board_complete", "board_source",
            "board_note", "registered", "registered_all", "registered_source",
            "voting_age", "voting_age_source", "voting_age_est", "voting_age_est_source",
            "president_votes", "president_source"]
    return d[cols]


if __name__ == "__main__":
    write(build(), "turnout")
