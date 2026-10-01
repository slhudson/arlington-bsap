"""The County's Resident Satisfaction Survey response file -> data/built/residents_survey.csv

The workbook as a table: one row per respondent, one column per question as
the sheet heads it, every value as printed ("1. Own", "Strongly Agree",
"Don't Know"). Headings keep the instrument's wording, typos and all, and
race and home language stay one column per option, because this stage
reshapes and never decides. code/clean/residents_survey.py names the items,
collapses the categories and says what a blank means.

The sheet carries one wholly empty row between the heading and the first
respondent; it is dropped, and the step refuses the file if a second
appears, since a blank row among the responses would mean something else.

    <the sheet's heading>   one column per question, verbatim
"""
import pandas as pd

from paths import RAW, source, write

WORKBOOK = RAW / "arlington_county" / "residents_survey_data.xlsx"

# What the published report counts, and so what this file must hold (zilo2026).
RESPONDENTS = 1613


def build() -> pd.DataFrame:
    sheet = source(WORKBOOK, dtype=str, keep_default_na=False)
    empty = sheet.index[(sheet == "").all(axis=1)]
    if len(empty) != 1:
        raise AssertionError(
            f"{WORKBOOK.name}: expected one empty row below the heading, found "
            f"{len(empty)} at {list(empty)}. An empty row among the responses is "
            f"not a spacer and dropping it would lose a respondent.")
    rows = sheet.drop(index=empty).reset_index(drop=True)
    if len(rows) != RESPONDENTS:
        raise AssertionError(
            f"{WORKBOOK.name}: {len(rows)} respondents, and zilo2026 reports "
            f"{RESPONDENTS}. The file is not the one the report describes.")
    return rows


if __name__ == "__main__":
    write(build(), "residents_survey")
