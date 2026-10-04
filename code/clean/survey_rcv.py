"""Ranked Choice Voting by group, as the figures read it -> data/clean/survey_rcv.csv

One row per group category per measure. The decision this step makes is what
to do with a cell its preparers marked `caution`: it is carried, with the
respondents behind it, rather than dropped. Hispanic respondents are 37 of
the 584 and two of their three measures are marked that way, and those are
the cells the report's claim about Latino voters turns on - dropping them
would answer the question by hiding it, and the figure says how thin they are
instead (docs/survey_rcv.md).

A `suppressed` cell has no share to carry and becomes blank.

    group, category, measure   as the source cuts them
    respondents                how many respondents the category holds
    share                      the weighted share, or points for net_support
    counted                    the unweighted number who answered that way
    thin                       whether the source marked the cell caution
"""
import numpy as np

import paths

SUPPRESSED = "suppressed"
CAUTION = "caution"


def clean():
    d = paths.typed(paths.built("survey_rcv")).rename(columns={"value": "share"})
    d["thin"] = d["status"] == CAUTION
    d.loc[d["status"] == SUPPRESSED, "share"] = np.nan
    out = d[["group", "category", "respondents", "measure", "share",
             "counted", "thin"]]
    kept = out[out["share"].notna()]
    if kept["thin"].all() or not kept["thin"].any():
        raise AssertionError(
            "every reportable cell is marked the same way, which the source "
            "does not do: check that status survived code/build/survey_rcv.py.")
    return out


if __name__ == "__main__":
    paths.write(clean(), "survey_rcv")
