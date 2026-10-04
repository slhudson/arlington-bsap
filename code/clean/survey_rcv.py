"""Ranked Choice Voting by group, as the figures read it -> data/clean/survey_rcv.csv

One row per question per group category per answer. The decision this step
makes is what to do with a cell its preparers marked `caution`: it is carried
and flagged `thin`, rather than dropped. Of the seven race and ethnicity
categories only White and Black are unflagged, and the thirty-seven Hispanic
respondents are among the rest - the cells the community-input analysis'
claim about Latino voters turns on, so dropping them would answer the
question by removing the evidence (docs/survey_rcv.md).

A `suppressed` cell has no share to carry and becomes blank.

    question, group, category, answer, kind   as the source cuts them
    respondents  how many the category holds
    share        the weighted share, or points where `unit` is points
    counted      how many gave this answer
    thin         whether the source marked the cell caution
"""
import numpy as np

import paths

SUPPRESSED = "suppressed"
CAUTION = "caution"


def clean():
    d = paths.typed(paths.built("survey_rcv")).rename(columns={"value": "share"})
    d["thin"] = d["status"] == CAUTION
    d.loc[d["status"] == SUPPRESSED, "share"] = np.nan
    out = d[["question", "group", "category", "answer", "kind",
             "respondents", "share", "counted", "thin"]]
    kept = out[out["share"].notna()]
    if kept["thin"].all() or not kept["thin"].any():
        raise AssertionError(
            "every reportable cell is marked the same way, which the source "
            "does not do: check that status survived code/build/survey_rcv.py.")
    return out


if __name__ == "__main__":
    paths.write(clean(), "survey_rcv")
