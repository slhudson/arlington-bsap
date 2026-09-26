"""Where Board members lived, claim by claim -> data/clean/board_residence.csv

Every claim in data/transcribed/by_claude/board_residence.csv, and the place
from each census record in board_census.csv through board_census.py, one row
per claim with its source, basis and quote, and how precisely the place is
named (PRECISION). Nothing is coded North or South and no claim is chosen
over another; docs/board.md has what is open. A member seated for a
magisterial district also gets a district claim from the office, source
`derived`: the project assumes a supervisor lived in the district he was
seated for, which the law required only from 1903 (docs/board.md, Residence
in the district).
"""
import re

import pandas as pd

import board_census
import paths
from paths import write

DISTRICTS = ("Arlington", "Jefferson", "Washington")

BASIS = ("derived from the office: the member was seated for this magisterial "
         "district, and a supervisor is assumed to have lived in the district "
         "he represented; no record about the person")


def district_claims(members: pd.DataFrame) -> pd.DataFrame:
    """One claim per person per district they were seated for, dated to the
    start of the first term there. An at-large seat names no place."""
    seated = members[members.district.isin(DISTRICTS)]
    first = seated.sort_values(["start_year", "start_month"]).drop_duplicates(["name", "district"])
    return pd.DataFrame({
        "name": first.name, "year": first.start_year.astype(int).astype(str),
        "place": first.district + " District", "basis": BASIS,
        "source": "derived", "quote": "", "precision": "district"})


# How exactly a place is named, most to least: a house on a street, a street
# with no house, a neighborhood or civic association, a side of the County,
# a magisterial district of Alexandria County (the 1880-1910 sheets, where
# the street column is blank). docs/board.md says where each line falls.
PRECISION = ("address", "street", "neighborhood", "side", "district")

_SIDE = re.compile(r"^(North|South) Arlington$|northernmost section", re.I)
_HOUSE = re.compile(r"^\d{3,5}\s|house number \d+|, number \d+")
_UNREAD = re.compile(r"abbreviation unread")
_HOOD_WORDS = re.compile(r"neighborhood|civic association|\barea\b|subdivision|community|^off ", re.I)
_STREET_WORDS = re.compile(r"\b(street|st\.?|road|rd\.?|blvd\.?|drive|avenue|ave\.?|pike)\b", re.I)
_HOODS = re.compile(r"^(Clarendon|Fairlington|Lyon Park|Aurora Hills|Livingstone Heights|"
                    r"East Falls Church|Dominion Hills|Donaldson Run|Tara-Leeway Heights|Cherrydale)(,|$)", re.I)
_DISTRICT = re.compile(r"^(Arlington|Jefferson|Washington)( Magisterial)?( District| Township)?( \((P|p)art( of)?\))?$")


def precision(place: str) -> str:
    """The precision of one place, from its words. A place no rule reads stops
    the build, so a new kind of place cannot quietly count as the wrong shade."""
    if _SIDE.search(place):
        return "side"
    if _HOUSE.search(place) and not _UNREAD.search(place):
        return "address"
    if _HOOD_WORDS.search(place) or _HOODS.match(place) or _UNREAD.search(place):
        return "neighborhood"
    if _STREET_WORDS.search(place) or re.match(r"^(No|So|North|South|N|S)\.? \w+", place):
        return "street"
    if _DISTRICT.match(place):
        return "district"
    raise ValueError(f"no precision rule reads this place: {place!r}")


def build() -> pd.DataFrame:
    c = paths.built("board_claims")
    stated = c.loc[c.claim == "residence", ["name", "year", "place", "basis", "source", "quote"]]
    claims = pd.concat([stated, board_census.residences()], ignore_index=True).fillna("")
    claims["precision"] = [precision(p) for p in claims.place]
    claims = pd.concat([claims, district_claims(paths.read("board_members"))],
                       ignore_index=True)
    return claims.sort_values(["name", "year"], kind="stable")


if __name__ == "__main__":
    write(build(), "board_residence")
