"""Question 3 across the three waves -> data/clean/survey_satisfaction_by_year.csv

One row per item per wave: the share rating it very satisfied or satisfied,
with don't knows excluded, which is the convention zilo2026 states and the
only one its chart can be read on.

Two decisions. A wave the chart marks "Not asked in 2022" has no value, and
stays blank rather than being carried forward from another wave. And two
items print the same figure in 2018 as in 2026, in a chart where no other
item repeats and where both are the ones not asked in 2022; `repeats_2026`
marks them so a figure can say so rather than drawing them as read
(docs/survey_satisfaction.md).

    item         the item as question 3 words it
    year         2018, 2022 or 2026
    satisfied    the share, in per cent, or blank where the item was not asked
    repeats_2026 whether this 2018 value equals the item's 2026 value
"""
import paths

WAVES = [2018, 2022, 2026]


def clean():
    d = paths.typed(paths.built("survey_satisfaction_by_year"))
    d = d[["item", "year", "satisfied"]].copy()
    if sorted(d.year.unique()) != WAVES:
        raise AssertionError(f"waves are {sorted(d.year.unique())}, not {WAVES}")
    in_2026 = d[d.year == 2026].set_index("item").satisfied
    d["repeats_2026"] = (d.year == 2018) & (d.satisfied == d.item.map(in_2026))
    return d.sort_values(["item", "year"], kind="stable").reset_index(drop=True)


if __name__ == "__main__":
    paths.write(clean(), "survey_satisfaction_by_year")
