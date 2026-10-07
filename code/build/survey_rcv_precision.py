"""What the survey's weights do to precision -> data/built/survey_rcv_precision.csv

One row per group category: how many respondents it holds, Kish's effective
sample size once the weights are counted, the design effect between them, and
the 95 per cent margin of error for a share near half. Carried as published;
nothing here is decided.

    group, category        as the source cuts them
    respondents            how many the category holds
    effective_respondents  (sum w)^2 / sum(w^2)
    design_effect          respondents / effective_respondents
    margin_points          the 95 per cent margin, with the design effect
"""
from paths import RCVA, source, write

TABLE = RCVA / "survey_rcv_precision.csv"

COLUMNS = {"group": "group", "category": "category", "n": "respondents",
           "n_effective": "effective_respondents", "design_effect": "design_effect",
           "moe_with_design_effect_pts": "margin_points"}


def build():
    d = source(TABLE, dtype=str, keep_default_na=False)
    return d[list(COLUMNS)].rename(columns=COLUMNS)


if __name__ == "__main__":
    write(build(), "survey_rcv_precision")
