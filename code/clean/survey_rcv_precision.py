"""The margin on a share from the 2025 survey -> data/clean/survey_rcv_precision.csv

One row per group category. The margin is the one the survey's own weights
imply, not the one a headcount would: 584 respondents behave like 360 once
the weights are counted, so the full sample carries five points and not four,
and a category of thirty-seven carries twenty (docs/survey_rcv.md).

The figures read `margin_points` and nothing else here; the effective count
and the design effect are carried so a reader can see where it comes from.
"""
import paths


def clean():
    d = paths.typed(paths.built("survey_rcv_precision"))
    if (d.margin_points <= 0).any() or (d.design_effect < 1).any():
        raise AssertionError(
            "a margin at or below zero, or a design effect under one, which "
            "weighting cannot produce: check code/build/survey_rcv_precision.py.")
    return d


if __name__ == "__main__":
    paths.write(clean(), "survey_rcv_precision")
