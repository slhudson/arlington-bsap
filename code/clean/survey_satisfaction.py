"""The Resident Satisfaction Survey, respondent by respondent -> data/clean/survey_satisfaction.csv

One row per respondent, 2026, holding the items the report reads and the
demographics it cuts them by. Every decision about what a value *is* is
made here; docs/survey_satisfaction.md has the reasoning.

The scale is kept as the instrument prints it, five points plus "Don't Know",
because collapsing it into a satisfied share is presentation and belongs in
code/analysis/. What this step settles is the three kinds of non-answer the
workbook does not distinguish for us - a blank, an explicit decline, and
"Don't Know" - and the collapse of eight race boxes into one category.

    respondent            its row in data/built/survey_satisfaction.csv, from 0
    familiar .. trust_manager    question 4, five-point agreement
    transparency, engagement     question 3, five-point satisfaction
    communication                question 1, five-point satisfaction
    tenure, years_resident, income, gender, race   the demographics
    demographics_declined        whether race, income and gender are all
                                 blank or declined
"""
import pandas as pd

import paths

DECLINED = "declined"

# Each item, as a phrase that appears in exactly one of the workbook's
# headings. Matched rather than numbered so a column moving is an error
# rather than a silent switch of items; the headings carry the
# instrument's typos.
ITEMS = {
    "familiar": "a. I am familiar with Arlington County",
    "structure_right": "b. Arlington County’s form of government and County Board structure are right",
    "trust_information": "c. I trust information that is provided",
    "trust_elected": "d. I trust Arlington County's elected officials",
    "trust_manager": "e. I trust the County Manager",
    "transparency": "h. Transparency of the County's decision-making process",
    "engagement": "g. Opportunities for public engagement with the County",
    "communication": "m. Effectiveness of the County’s communication with the public",
    "tenure": "Do you own or rent your current home?",
    "years_resident": "how many years have you lived in Arlington County?",
    "income": "What is your total annual household income?",
    "gender": "What gender do you most identify with?",
}

# The race boxes, in the order the instrument lists them.
RACE = {
    "asian": "race or ethnicity? 1. Asian",
    "black": "race or ethnicity? 2. Black",
    "hispanic": "race or ethnicity? 3. Hispanic",
    "amind": "race or ethnicity? 4. Native American",
    "white": "race or ethnicity? 5. White",
    "nhpi": "race or ethnicity? 6. Native Hawaiian",
    "declined": "race or ethnicity? 7. Prefer not",
    "other": "Which of the following best describes your race or ethnicity? "
             "8. Other (please specify)",
}


def column(frame: pd.DataFrame, phrase: str) -> pd.Series:
    """The one column whose heading contains `phrase`."""
    hit = [c for c in frame.columns if phrase in c]
    if len(hit) > 1 and phrase in hit:
        return frame[phrase]          # a heading another one extends, named in full
    if len(hit) != 1:
        raise AssertionError(
            f"{phrase!r} matches {len(hit)} headings in the workbook, not one. "
            f"The instrument has changed; check code/clean/survey_satisfaction.py "
            f"against data/built/survey_satisfaction.csv.")
    return frame[hit[0]]


def printed(values: pd.Series) -> pd.Series:
    """A value without the option number the instrument prints in front of
    it: "1. Own" is Own. An explicit refusal becomes `declined`, so a
    refusal and a blank are never read as the same thing."""
    bare = values.str.replace(r"^\s*\d+\.\s*", "", regex=True).str.strip()
    return bare.where(~bare.str.lower().str.startswith("prefer not"), DECLINED)


def race(frame: pd.DataFrame) -> pd.Series:
    """The eight race boxes as one category, cut the way the census crosses
    its two questions, so the survey and data/clean/residents.csv can be set
    side by side: Hispanic of any race first, then among the rest White,
    Black, Asian and Pacific Islander, and everyone else together
    (docs/residents.md). A respondent naming two races is therefore
    `other_or_multiracial` unless one of them is Hispanic."""
    box = pd.DataFrame({k: column(frame, p) != "" for k, p in RACE.items()})
    named = box[["asian", "black", "hispanic", "amind", "white", "nhpi", "other"]]
    out = pd.Series("", index=frame.index)
    out[box.declined] = DECLINED          # a box checked, before any race is read
    out[named.sum(axis=1) > 1] = "other_or_multiracial"
    for one, label in [("other", "other_or_multiracial"), ("amind", "other_or_multiracial"),
                       ("nhpi", "aapi"), ("asian", "aapi"),
                       ("black", "black"), ("white", "white")]:
        out[(named.sum(axis=1) == 1) & named[one]] = label
    out[box.hispanic] = "hispanic"        # of any race, so it is read last
    return out


def clean() -> pd.DataFrame:
    sheet = paths.built("survey_satisfaction")
    out = pd.DataFrame({"respondent": range(len(sheet))})
    for name, phrase in ITEMS.items():
        out[name] = printed(column(sheet, phrase)).values
    out["race"] = race(sheet).values
    out["demographics_declined"] = (
        out[["race", "income", "gender"]].isin(["", DECLINED]).all(axis=1))
    return out


if __name__ == "__main__":
    paths.write(clean(), "survey_satisfaction")
