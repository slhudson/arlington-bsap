"""Race and gender of every Board member -> data/clean/board_demographics.csv

One row per person in the roster. Race and gender come from
data/transcribed/by_claude/board_demographics.csv, which holds only the
people a source says something about, in the source's own words. Everyone
else is a white man by default, and the row says so: `basis` reads "default"
and the source columns are empty. The default is a claim, not a finding -
docs/sources.md says what stands behind it in each period.

A person can carry more than one attribution - Syphax is identified by both
Hjerpe and O'Leary, independently. All are kept, joined with semicolons,
rather than one chosen and the rest lost. Two sources disagreeing on a
category would be a finding worth stopping for, so the build refuses it.

Every attributed name must match a roster name exactly. A near-miss
("Bozman" for "Ellen Bozman") would silently fall into the default, which is
the one failure this file exists to prevent, so the build refuses that too.
"""
import pandas as pd

from files import CLEAN, TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"


def build() -> pd.DataFrame:
    roster = pd.read_csv(CLEAN / "board_roster.csv")
    people = (roster.sort_values(["start_year", "start_month"])
              .groupby("name", sort=False)
              .agg(first_year=("start_year", "min"), last_year=("end_year", "max"))
              .reset_index())

    a = pd.read_csv(BY_CLAUDE / "board_demographics.csv").fillna("")
    unknown = sorted(set(a.name) - set(people.name))
    if unknown:
        raise ValueError("attributed names not in the roster (spelling must match exactly):\n"
                         + "\n".join(f"  {n!r}" for n in unknown))

    def one(values):
        vals = sorted(set(v for v in values if v))
        if len(vals) > 1:
            raise ValueError(f"sources disagree: {vals}")
        return vals[0] if vals else ""

    # Race and gender are attributed separately: a woman known from her
    # printed name has a source for her gender and none for her race, and
    # the row must say so field by field.
    def fold(rows):
        return pd.Series({
            "race": one(rows.race), "gender": one(rows.gender),
            "race_basis": "; ".join(rows.basis[rows.race != ""]),
            "race_source": "; ".join(rows.source[rows.race != ""]),
            "gender_basis": "; ".join(rows.basis[rows.gender != ""]),
            "gender_source": "; ".join(rows.source[rows.gender != ""]),
            "quote": " | ".join(rows.quote),
        })
    by_person = a.groupby("name").apply(fold, include_groups=False)

    d = people.merge(by_person, left_on="name", right_index=True, how="left").fillna("")
    for field, default in (("race", "White"), ("gender", "man")):
        blank = d[field] == ""
        d.loc[blank, field] = default
        d.loc[blank, f"{field}_basis"] = "default"
    return d[["name", "first_year", "last_year", "race", "race_basis", "race_source",
              "gender", "gender_basis", "gender_source", "quote"]]


if __name__ == "__main__":
    write(build(), "board_demographics")
