"""Black candidacies for the Board, and the 1931 candidate list -> data/built/board_candidacies.csv

Two files under data/transcribed/by_claude/ stacked into one table, each
cell as keyed in, with `claim` saying which a row came from:

    candidacy   board_candidacies.csv: one row per candidacy a source states
                is a Black candidate's, in the source's words, or, with the
                name blank, a period in which a source says none ran
    listed      anderson_candidates_1931.csv: the county's list of the 51
                candidates for the November 1931 election, as Anderson
                reprints it, each entry as printed with its mark

Nothing is matched or decided here; code/clean/board_candidacies.py joins
each candidacy to its election. docs/board.md, "Black candidacies", has
what each column holds.
"""
import pandas as pd

from paths import BY_CLAUDE, source, write

FILES = {"candidacy": BY_CLAUDE / "board_candidacies.csv",
         "listed": BY_CLAUDE / "arlington_historical_magazine" / "anderson_candidates_1931.csv"}

COLUMNS = ["claim", "name", "year", "through", "election", "office", "race_words", "basis",
           "source", "page", "quote", "entry", "place", "note"]

# The list is the page Anderson prints; its rows carry no source column.
LISTED_SOURCE = "anderson1958"


def build() -> pd.DataFrame:
    parts = []
    for claim, path in FILES.items():
        d = source(path, dtype=str, keep_default_na=False)
        if claim == "listed":
            d = d.assign(year="1931", source=LISTED_SOURCE)
        parts.append(d.assign(claim=claim))
    return pd.concat(parts, ignore_index=True).reindex(columns=COLUMNS).fillna("")


if __name__ == "__main__":
    write(build(), "board_candidacies")
