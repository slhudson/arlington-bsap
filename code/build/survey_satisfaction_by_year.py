"""The published trend chart, keyed in -> data/built/survey_satisfaction_by_year.csv

Question 3's eleven items across 2026, 2022 and 2018, read off the chart
image on page 83 of zilo2026 and keyed into data/transcribed/by_claude/. This
step carries the table into the stages that may read it; nothing is reshaped
and nothing is decided. What a blank 2022 cell means, and whether the two
2018 values that repeat their 2026 ones are the 2018 values, are settled in
code/clean/survey_satisfaction_by_year.py.

    item, year, satisfied, source, note   as the transcription holds them
"""
from paths import BY_CLAUDE, source, write

TABLE = BY_CLAUDE / "survey_satisfaction_by_year.csv"


def build():
    return source(TABLE, dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "survey_satisfaction_by_year")
