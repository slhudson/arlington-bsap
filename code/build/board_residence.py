"""Where Board members lived, claim by claim -> data/clean/board_residence.csv

Every claim in data/transcribed/by_claude/board_residence.csv, and the place
from each census record in board_census.csv through board_census.py, one row
per claim with its source, basis and quote. Nothing is coded North or South
and no claim is chosen over another; docs/board.md has what is open.
"""
import pandas as pd

import board_census
from paths import BY_CLAUDE, write

CLAIMS = BY_CLAUDE / "board_residence.csv"


def build() -> pd.DataFrame:
    claims = pd.concat([pd.read_csv(CLAIMS, dtype=str), board_census.residences()],
                       ignore_index=True).fillna("")
    return claims.sort_values(["name", "year"], kind="stable")


if __name__ == "__main__":
    write(build(), "board_residence")
