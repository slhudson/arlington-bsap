r"""Numbers the prose cites that no figure carries -> paper/body_text_numbers.tex

One \newcommand per number, for the paper's preamble to \input. A name is
<measure><District><Year>, the year in words because a LaTeX command name
holds letters only, and a value is printed as the paper prints a share: a
whole number, with "percent" left to the sentence.

    share<District><Year>       the district's share of the county, 1870-1930
    blackShare<District><Year>  the Black share of the district, 1870 and 1920
    genderCensusShareMembers    members whose gender comes from a census sheet
    raceAssumedShareMembers     members recorded White on no source's say
    turnout<Year>               votes for President per 100 residents of voting
                                age, each presidential year 1880-1928
    boardTurnout<District><Year>  votes in a district's Board contest per 100
                                men of voting age, each contest with a count

    Jefferson held \shareJeffersonEighteenSeventy{} percent of the county.

The {} keeps the space after the command. Every number the table gives is
written, whether or not the prose uses it yet.
"""
from decimal import ROUND_HALF_UP, Decimal

import paths
from elections import per_100_adults, per_100_district_men

ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def year_words(year: int) -> str:
    """1900 -> NineteenHundred, 1904 -> NineteenFour, 1928 -> NineteenTwentyEight:
    the year as it is said, in letters, for a command name."""
    century, rest = divmod(int(year), 100)
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
    """The rates the two pre-1932 turnout figures draw, by the same arithmetic
    (code/analysis/elections.py): the presidential vote per 100 residents of
    voting age for each election 1880-1928, and each district's Board contest
    per 100 men of voting age for each contest with a count, 1893-1919."""
    adults = paths.read("residents_by_district_adults")
    president = paths.read("elections_results")
    president = president[(president.office == "president")
                          & president.year.between(1880, 1928)].set_index("year")
    out = {f"turnout{year_words(y)}": whole(v)
           for y, v in per_100_adults(president.total, adults).items()}
    contests = paths.read("elections_margins")
    contests = contests[contests.contest.str.endswith("District") & contests.votes_cast.notna()
                        & contests.year.between(1893, 1919)]
    for district in ("Arlington", "Jefferson", "Washington"):
        votes = contests[contests.contest == f"{district} District"].set_index("year").votes_cast
        for y, v in per_100_district_men(votes, district, adults).items():
            out[f"boardTurnout{district}{year_words(y)}"] = whole(v)
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
    out.update(member_shares())
    out.update(turnout())
    return out


def tex(values: dict) -> str:
    lines = ["% Generated by code/analysis/body_text_numbers.py from data/clean/.",
             "% Never edit by hand: bash run.sh rewrites it.", ""]
    for name, value in values.items():
        lines.append(f"\\newcommand{{\\{name}}}{{{value}}}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    paths.BODY_TEXT_NUMBERS.write_text(tex(numbers()))
