r"""Numbers the prose cites that no figure carries -> paper/body_text_numbers.tex

One \newcommand per number, for the paper's preamble to \input. A name is
<measure><District><Year>, the year in words because a LaTeX command name
holds letters only, and a value is printed as the paper prints a share: a
whole number, with "percent" left to the sentence.

    share<District><Year>       the district's share of the county, 1870-1930
    blackShare<District><Year>  the Black share of the district, 1870 and 1920
    blackShareMen<District><Year>  the Black share of the district's men 21 and
                                over, each census whose schedules are held
    genderCensusShareMembers    members whose gender comes from a census sheet
    raceAssumedShareMembers     members recorded White on no source's say
    turnout<Year>               votes for President per 100 residents of voting
                                age, each presidential year 1872-1928
    boardTurnout<District><Year>  votes in a district's Board contest per 100
                                men of voting age, each contest with a count
    boardVote<Year>             votes for the Board per 100 residents of voting
                                age, a one-seat year after 1971: the ones the
                                prose sets side by side
    residentsPerSeat<Year>      residents per Board seat, to the nearest thousand
    perMember<Locality>         residents per member of a Virginia locality's
                                governing body, 2020, to the nearest thousand
    southeastPlaces             the other cities and counties of 150,000 to
                                300,000 in the southeastern comparison
    southeastMore               of them, those with more residents per member,
                                spelled out
    groupShare<Group>TwoThousandTwenty   a group's share of the county's residents
    districtMajorityTwoThousandTwenty    residents a majority of one of five equal
                                districts takes, to the nearest thousand
    districtNeed<Group>TwoThousandTwenty the share of the county's residents in a
                                group that such a majority would take

    Jefferson held \shareJeffersonEighteenSeventy{} percent of the county.

The {} keeps the space after the command. Every number the table gives is
written, whether or not the prose uses it yet.
"""
from decimal import ROUND_HALF_UP, Decimal

import paths
import style
from elections import per_100_adults, per_100_district_men, per_100_voting_age

BOARD_VOTE_YEARS = (2012, 2013)   # a presidential year and the governor's year after it

ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def year_words(year: int) -> str:
    """1900 -> NineteenHundred, 1904 -> NineteenFour, 1928 -> NineteenTwentyEight:
    the year as it is said, in letters, for a command name."""
    century, rest = divmod(int(year), 100)
    if century == 20:                      # 2020 -> TwoThousandTwenty
        return "TwoThousand" + (TENS[rest // 10] + ONES[rest % 10] if rest >= 20 else ONES[rest])
    if rest == 0:
        tail = "Hundred"
    elif rest < 20:
        tail = ONES[rest]
    else:
        tail = TENS[rest // 10] + ONES[rest % 10]
    return ONES[century] + tail


def per_cent(part, whole) -> str:
    """A share as the paper prints it: a whole number, halves rounded up."""
    return str((Decimal(int(part)) * 100 / Decimal(int(whole))).quantize(0, ROUND_HALF_UP))


def whole(rate) -> str:
    """A rate per 100 as the paper prints it: a whole number, halves rounded up."""
    return str(Decimal(float(rate)).quantize(0, ROUND_HALF_UP))


def thousands(x) -> str:
    """A count to the nearest thousand, as the paper prints it: 47729 -> 48,000."""
    return f"{int(Decimal(float(x) / 1000).quantize(0, ROUND_HALF_UP)) * 1000:,}"


def seats() -> dict:
    """The seat comparisons Part C's Board Seats draws, against Arlington's own
    past and against two sets of peers. Each claim the prose makes about a set
    is asserted here, so a data change that falsifies a sentence stops the
    build instead of printing."""
    r = paths.read("residents").set_index("year").residents_per_seat
    out = {f"residentsPerSeat{year_words(y)}": thousands(r[y]) for y in (1870, 2020)}

    va = paths.read("localities")
    va = va[va.residents >= 100_000].copy()
    va["per"] = va.residents / va.members
    me = va[va.locality == "Arlington"].iloc[0]
    for name in ("Arlington", "Loudoun", "VirginiaBeach", "Norfolk", "Chesapeake"):
        row = va[va.locality.str.replace(" ", "") == name].iloc[0]
        out[f"perMember{name}"] = thousands(row.per)
    above = va[va.per > me.per]
    assert (above.kind == "county").all() and (above.residents > me.residents).all(), \
        "the Virginia places above Arlington are no longer all larger counties"
    its_size = va[(va.kind == "city") & va.residents.between(0.9 * me.residents,
                                                             1.1 * me.residents)]
    assert len(its_size) and (its_size.per < me.per).all(), \
        "a city of Arlington's size now carries more residents per member"

    se = paths.read("localities_southeastern")
    se["per"] = se.residents / se.members
    se = se[se.locality != "Arlington"]
    above = se[se.per > me.per]
    assert (above.kind == "county").all() and (above.members <= 5).all(), \
        "the southeastern places above Arlington are no longer all counties of five seats or fewer"
    assert (se[se.kind == "city"].per < me.per).all(), "a southeastern city now carries more"
    out["southeastPlaces"] = str(len(se))
    out["southeastMore"] = ONES[len(above)].lower()
    return out


def groups() -> dict:
    """What a district majority would ask of each group in 2020, the arithmetic
    behind Part C's claim that districts alone would give none of them a seat.
    The Board's five seats cut the county into five equal districts, and a
    majority of one is more than half of its residents. Black residents number
    fewer than that, so no district of any plan of five can be majority Black;
    the other two would need most of the county's residents of the group to
    live in one district. The assertions stop the build if the counts change
    what the sentence says."""
    r = paths.read("residents").set_index("year").loc[2020]
    district = r.total / r.board_seats
    majority = int(district // 2) + 1
    out = {"districtMajorityTwoThousandTwenty": thousands(majority)}
    for name, column in (("Black", "black"), ("Hispanic", "hisp"), ("Asian", "aapi")):
        assert r[column] < r.total / 2, f"{name} residents are now a majority of the county"
        out[f"groupShare{name}TwoThousandTwenty"] = per_cent(r[column], r.total)
    assert r.black < majority, "Black residents could now fill a district of five"
    for name, column in (("Hispanic", "hisp"), ("Asian", "aapi")):
        need = majority / r[column]
        assert 0.5 < need < 1, f"a {name} majority district no longer takes most of the group"
        out[f"districtNeed{name}TwoThousandTwenty"] = whole(need * 100)
    return out


def member_shares() -> dict:
    """How members, not seat-years, are known: one row per person, by name.

    genderCensusShareMembers   share of all members whose gender comes from a
                                census sheet, the rest read from the press
    raceAssumedShareMembers    share of all members recorded White because no
                                source says otherwise
    membersTotal               people who have served, one per name
    birthYearMissingMembers    of them, those with no birth year found
    notWhiteMenMembers         of them, those who were a woman, or not White, or both
    whiteMenMembers            the rest
    """
    m = paths.read("members").drop_duplicates(subset="name")
    not_white_men = int(((m.gender != "man") | (m.race != "White")).sum())
    return {
        "notWhiteMenMembers": str(not_white_men),
        "whiteMenMembers": str(len(m) - not_white_men),
        "genderCensusShareMembers": per_cent(m.gender_source.str.contains("census").sum(), len(m)),
        "raceAssumedShareMembers": per_cent((m.race_source == "assumed").sum(), len(m)),
        "membersTotal": str(len(m)),
        "birthYearMissingMembers": str(int(m.birth_year.isna().sum())),
    }


def turnout() -> dict:
    """The rates the turnout figure draws, by the same arithmetic
    (code/analysis/elections.py): the presidential vote per 100 residents of
    voting age for each election 1872-1928, each district's Board contest per
    100 men of voting age for each contest with a count, 1893-1919, and the
    Board's vote per 100 residents of voting age in the years the prose sets
    a presidential year beside a governor's."""
    adults = paths.read("residents_by_district_adults")
    president = paths.read("elections_results")
    president = president[(president.office == "president")
                          & president.year.between(1872, 1928)].set_index("year")
    out = {f"turnout{year_words(y)}": whole(v)
           for y, v in per_100_adults(president.total, adults).items()}
    contests = paths.read("elections_margins")
    contests = contests[contests.contest.str.endswith("District") & contests.votes_cast.notna()
                        & contests.year.between(1893, 1919)]
    for district in ("Arlington", "Jefferson", "Washington"):
        votes = contests[contests.contest == f"{district} District"].set_index("year").votes_cast
        for y, v in per_100_district_men(votes, district, adults).items():
            out[f"boardTurnout{district}{year_words(y)}"] = whole(v)
    t = paths.read("elections_turnout").set_index("year")
    for y in BOARD_VOTE_YEARS:
        assert t.board_seats[y] == 1 and t.board_complete[y], f"{y}'s Board vote is not one seat's"
        out[f"boardVote{year_words(y)}"] = whole(
            per_100_voting_age(t.board_voters[[y]], adults, t.voting_age_est).iloc[0])
    # Each presidential year's Board vote against the governor's year after
    # it, in the years both filled one seat. The prose says the first is
    # always higher, so a pair that is not stops the build.
    one_seat = t[(t.board_seats == 1) & t.board_complete.eq(True) & (t.index >= 1935)]
    rate = one_seat.board_voters / one_seat.voting_age_est * 100
    pairs = [(y, y + 1) for y in rate.index if y % 4 == 0 and y + 1 in rate.index]
    assert all(rate[a] > rate[b] for a, b in pairs), "a governor's year now out-polls the presidential year before it"
    out["boardPairs"] = str(len(pairs))
    out["boardPairsFirst"] = str(pairs[0][0])
    out["boardPairsLast"] = str(pairs[-1][0])
    return out


def numbers() -> dict:
    """Every command's name and value, in the order the file lists them."""
    d = paths.read("residents_by_district")
    out = {}
    for year, g in d.groupby("year"):
        for r in g.itertuples():
            out[f"share{r.district}{year_words(year)}"] = per_cent(r.total, g.total.sum())
    for r in d[d.black.notna()].itertuples():
        out[f"blackShare{r.district}{year_words(r.year)}"] = per_cent(r.black, r.total)
    men = paths.read("residents_by_district_adults")
    for r in men[men.district.isin(style.DISTRICTS) & men.men_black.notna()].itertuples():
        out[f"blackShareMen{r.district}{year_words(r.year)}"] = per_cent(r.men_black, r.men_all)
    out.update(member_shares())
    out.update(turnout())
    out.update(seats())
    out.update(groups())
    return out


def tex(values: dict) -> str:
    lines = ["% Generated by code/analysis/body_text_numbers.py from data/clean/.",
             "% Never edit by hand: bash run.sh rewrites it.", ""]
    for name, value in values.items():
        lines.append(f"\\newcommand{{\\{name}}}{{{value}}}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    paths.BODY_TEXT_NUMBERS.write_text(tex(numbers()))
