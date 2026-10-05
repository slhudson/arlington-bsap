"""Where the Gazette's own district return outranks the Almanack's county
figure for President, in force for YEARS -> replaces two rows elections_results.py
builds from state_return().

Mechanism only; the reasoning is in docs/elections.md, "The Gazette's own
district returns settle four of the nine," and the open question is
docs/questions.csv, gazette-vs-almanack-1892-1900. When the question is
settled, this moves into elections_results.py's state_return() and is
deleted.
"""
import pandas as pd

import elections

# Years where the Gazette's own district sum, read off the page image and
# tying to O'Leary's figure independent of him, replaces the Almanack's
# county total for the same election.
YEARS = {1892, 1900}


def gazette_sum(year: int) -> dict:
    """The Gazette's district rows for `year`, summed by party, with the
    citekey every row of that year shares."""
    g = elections.gazette_return()
    g = g[g.year == year]
    return {"dem": int(g[g.party == "Democratic"].votes.sum()),
            "rep": int(g[g.party == "Republican"].votes.sum()),
            "source": g.source.iloc[0]}


def apply(state_return: pd.DataFrame) -> pd.DataFrame:
    """Replace `dem` and `rep` for YEARS with the Gazette's district sum,
    widen `total` to match, add the Gazette's citekey to `source`, and note
    it; `other` is kept from the Almanack, since the Gazette's tables print
    no minor-ticket column."""
    out = state_return.copy()
    for year in YEARS:
        i = out.index[out.year == year]
        if not len(i):
            continue
        i = i[0]
        sums = gazette_sum(year)
        out.loc[i, ["dem", "rep"]] = sums["dem"], sums["rep"]
        out.loc[i, "total"] = sums["dem"] + sums["rep"] + out.loc[i, "other"]
        out.loc[i, "source"] = f"{out.loc[i, 'source']}; {sums['source']}"
        out.loc[i, "note"] = ("dem and rep are the Gazette's own district return, which "
                              "replaces the Almanack's county figure; docs/elections.md")
    return out
