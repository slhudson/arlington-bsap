"""Where Board members lived, claim by claim -> data/clean/board_residence.csv

Every claim in data/transcribed/by_claude/board_residence.csv, and the place
from each census record in board_census.csv through board_census.py, one row
per claim with its source, basis and quote, and how precisely the place is
named (PRECISION). Nothing is coded North or South and no claim is chosen
over another; docs/board.md has what is open.
"""
import re

import pandas as pd

import board_census
from paths import BY_CLAUDE, write

CLAIMS = BY_CLAUDE / "board_residence.csv"

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
    claims = pd.concat([pd.read_csv(CLAIMS, dtype=str), board_census.residences()],
                       ignore_index=True).fillna("")
    claims["precision"] = [precision(p) for p in claims.place]
    return claims.sort_values(["name", "year"], kind="stable")


if __name__ == "__main__":
    write(build(), "board_residence")
