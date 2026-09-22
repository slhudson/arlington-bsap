"""raw/ member database -> data/board_members.csv

One row per member per year, 1932-2026. Person-level, where board_seats.csv is
year-level; the two cover different periods, which is docs/questions.md Q4.

No figure uses this yet. It is built so the descriptive coding has a home, and
so a source column can be added per docs/sources.md recording what backs each
race and gender assignment.
"""
import pandas as pd

from files import BOARD_MEMBERS_XLSX, write


def build() -> pd.DataFrame:
    r = pd.read_excel(BOARD_MEMBERS_XLSX)
    r.columns = [c.strip().lower().replace("/", "_") for c in r.columns]
    return r


if __name__ == "__main__":
    write(build(), "board_members")
