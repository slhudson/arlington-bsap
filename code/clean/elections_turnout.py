"""Who votes for the County Board, year by year -> data/clean/elections_turnout.csv

One row per year in which any of these is measured, 1872-2025:

  board_votes      every vote cast in the November County Board contests,
                   write-ins included, and board_seats, how many seats
                   they filled
  board_voters     votes divided by seats: the people that represents,
                   exactly for one seat and a lower bound for two or more
  registered       Arlington's active registered voters at that November's
                   election, from 2010; registered_all adds the inactive
  voting_age       the population 18 and over in a census year, from 1970
  voting_age_21    the population 21 and over in a census year, 1930-1970
  voting_age_est   the population old enough to vote that November: 21 and
                   over through 1970, 18 and over from 1971, when the
                   Twenty-sixth Amendment took effect; carried between
                   censuses
  president_votes  the county's presidential vote, from elections_results.csv
  cycle            what else the November ballot carried, from 1931

Each measure has its own `_source` column. The seats an election filled
are counted from the roster: terms an election seated the next January, or
a special election that November. A year is marked incomplete on the rule
in elections.contest_rows(). docs/elections.md has the reasoning.

Three guards: the Board's voters never exceed the registered voters, nor
the presidential vote of the same year, and the registered never exceed
the adults.
"""
import pandas as pd

import members_terms
import census
import citekeys
import elections
import paths
import residents
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
# 1930-1970, printed lines of the census volume's county age table, which
# residents.volume_table() checks: the population 21 and over, and in 1970
# the population 18 and over, read from the single years.
VOLUME_VOTING_AGE_21 = {1930: ["Males 21 years old and over", "Females 21 years old and over"],
                        1940: ["21 years and over"], 1950: ["21 years and over"], 1960: ["21 AND OVER"], 1970: ["21 years and over"]}
VOLUME_VOTING_AGE = {1970: ["18 years", "19 years", "20 years", "21 years and over"]}
# The first November at which 18-year-olds voted.
VOTE_AT_18 = 1971
# The year's place in Virginia's four-year cycle, by year mod 4.
CYCLE = {0: "president", 1: "governor", 2: "midterm", 3: "delegates"}


def seats_filled(roster: pd.DataFrame, year: int) -> int:
    """Seats the November election of `year` filled: terms an election
    seated the next January, or a special election seated that November."""
    regular = ((roster.seated_by == members_terms.ELECTION)
               & (roster.start_year == year + 1) & (roster.start_month == 1))
    special = ((roster.seated_by == members_terms.SPECIAL_ELECTION)
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
            votes, seats = named.votes.sum(), seats_filled(roster, year)
            source = named.source.iloc[0]
            if not named.source.str.startswith(citekeys.ARLINGTON_ELECTIONS).all():
                source = "; ".join(dict.fromkeys(named.source))    # a filled blank cites its newspaper
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
    """1870-1915: the elections, May or November, with a count for every
    candidate in all three districts, from the Gazette's own returns
    (candidates_gazette); 1907 and 1915 agree with O'Leary's to the vote, so
    nothing rests on him here (docs/elections.md, "Which years are not the
    county's vote")."""
    g = paths.typed(paths.built("candidates_gazette"))
    rows = []
    for year, h in g.groupby("year"):
        if h.district.nunique() != 3 or h.votes.isna().any():
            continue
        if h.groupby("district").votes.count().min() < 2:
            continue    # an unopposed seat counts who bothered, not who could vote
        rows.append({"year": int(year), "board_votes": int(h.votes.sum()), "board_seats": 3,
                     "board_complete": True,
                     "board_source": f"{h.source.iloc[0]} p.{h.page.iloc[0]}",
                     "board_note": "one seat per district, so one vote per voter"})
    if not rows:
        raise AssertionError("no district election with a count in every district - "
                             "1907 and 1915 should be there")
    return pd.DataFrame(rows).sort_values("year", ignore_index=True)


def registration() -> pd.DataFrame:
    r = paths.typed(paths.built("registration"))
    return pd.DataFrame({
        "year": r.year, "registered": r.active, "registered_all": r["all"],
        "registered_source": [f"{citekeys.VA_REGISTRATION} {rep}" + (f", as of {d}" if isinstance(d, str) else "")
                              for rep, d in zip(r.report, r.as_of)]})


def voting_age() -> pd.DataFrame:
    rows = []
    for year, (file, cols) in VOTING_AGE.items():
        r = census.row("us_census_bureau/" + file)
        if cols == "from 18":
            ages = list(r.index[3:])
            cols = ages[ages.index("18"):]
            assert ages[0] == "under_1" and cols[-1] == "85_over", ages
        rows.append({"year": year, "voting_age": int(r[cols].sum()),
                     "voting_age_source": f"{VOTING_AGE_SOURCE.get(year, citekeys.CENSUS_DATA_FILE)} "
                                          f"{file.split('/')[1]}"})
    for year, lines in VOLUME_VOTING_AGE.items():
        t = residents.volume_table(year)
        rows.append({"year": year, "voting_age": int(t.loc[lines, "total"].sum()),
                     "voting_age_source": "; ".join(t.loc[lines, "cite"].unique())})
    return pd.DataFrame(rows)


def voting_age_21() -> pd.DataFrame:
    rows = []
    for year, lines in VOLUME_VOTING_AGE_21.items():
        t = residents.volume_table(year)
        rows.append({"year": year, "voting_age_21": int(t.loc[lines, "total"].sum()),
                     "voting_age_21_source": "; ".join(t.loc[lines, "cite"].unique())})
    return pd.DataFrame(rows)


def carried(d: pd.DataFrame, col: str) -> pd.Series:
    """A census count in every year from the first census that reports it:
    a straight line between censuses, the last carried forward."""
    known = d.dropna(subset=[col]).set_index("year")[col]
    est = pd.Series(index=d.year.to_numpy(), dtype=float)
    est.loc[known.index] = known.to_numpy(dtype=float)
    est = est.interpolate(method="index").ffill()
    est[est.index < known.index.min()] = float("nan")
    return est


def between_censuses(d: pd.DataFrame) -> pd.Series:
    """The population old enough to vote each November: 21 and over through
    1970, carried between the censuses that print it, and 18 and over from
    1971, carried from 1970 on."""
    under_21, from_18 = carried(d, "voting_age_21"), carried(d, "voting_age")
    return under_21.where(under_21.index < VOTE_AT_18, from_18).to_numpy()


def president() -> pd.DataFrame:
    v = read("elections_results")
    v = v[(v.office == "president") & v.complete]
    return pd.DataFrame({"year": v.year, "president_votes": v.total,
                         "president_source": citekeys.DERIVED})


def build() -> pd.DataFrame:
    roster = read("members")
    board = pd.concat([board_districts(), board_votes(roster)], ignore_index=True)
    # The whole Board was elected every fourth year until terms were
    # staggered from 1940; from then on a seat is filled every November.
    years = list(board[board.year >= 1931].year)
    assert years == [1931, 1935, 1939] + list(range(1940, members_terms.PRESENT)), \
        f"a November Board contest is missing or extra: {years}"
    board["board_voters"] = (board.board_votes / board.board_seats).round().astype(int)
    # A district seat is its own contest and a voter votes in one district:
    # every vote is a voter, whatever the three contests add up to.
    district_era = board.year < 1931
    board.loc[district_era, "board_voters"] = board.board_votes[district_era]

    d = board
    for part in (registration(), voting_age(), voting_age_21(), president()):
        d = d.merge(part, on="year", how="outer")
    d = d.sort_values("year").reset_index(drop=True)
    d["cycle"] = [CYCLE[y % 4] if y >= 1931 else "" for y in d.year]
    d["voting_age_est"] = between_censuses(d)
    d["voting_age_est_source"] = [citekeys.DERIVED if pd.notna(v) else "" for v in d.voting_age_est]

    # Two independent reads of the same figure. voting_age comes from each
    # census's race-by-18-and-over table, and in 1970 from the printed single
    # years; residents.csv builds the adult population by summing six age
    # bands out of the sex-by-age table, and in 1970 out of the printed
    # five-year groups. They must agree exactly.
    bands = read("residents").set_index("year")[list(residents.ADULT_BANDS)]
    adults = bands.dropna().sum(axis=1)
    for year, here in d.dropna(subset=["voting_age"]).set_index("year").voting_age.items():
        there = adults.get(year)
        assert there is not None and int(here) == int(there), (
            f"{year}: the 18-and-over table gives {int(here):,} adults and the "
            f"age bands in residents.csv give "
            f"{'no row' if there is None else format(int(there), ',')}")

    for a, b, what in (("board_voters", "registered", "more Board voters than registered voters"),
                       ("board_voters", "president_votes", "more Board voters than presidential voters"),
                       ("registered", "voting_age_est", "more registered voters than adults")):
        both = d.dropna(subset=[a, b])
        over = both[both[a] > both[b]]
        assert over.empty, f"{what} in {list(over.year)}"

    for c in ("board_votes", "board_seats", "board_voters", "registered", "registered_all",
              "voting_age", "voting_age_21", "voting_age_est", "president_votes"):
        d[c] = d[c].round().astype("Int64")
    for c in ("board_source", "board_note", "registered_source", "voting_age_source",
              "voting_age_21_source", "president_source"):
        d[c] = d[c].fillna("")
    cols = ["year", "cycle", "board_votes", "board_seats", "board_voters", "board_complete", "board_source",
            "board_note", "registered", "registered_all", "registered_source",
            "voting_age", "voting_age_source", "voting_age_21", "voting_age_21_source",
            "voting_age_est", "voting_age_est_source",
            "president_votes", "president_source"]
    return d[cols]


if __name__ == "__main__":
    write(build(), "elections_turnout")
