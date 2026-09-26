"""ASSUMPTION, in force until `residence-district` in docs/questions.csv is
settled: a member seated for a magisterial district lived in it.

Sec. 32 of the 1902 constitution makes a voter eligible to an office of a
subdivision "wherein he resides", so from 1903 this is the rule. Before that
neither the 1869 constitution nor the 1873 Code has been read for it
(docs/board.md). When it is settled, this moves into board_residence.py or
is dropped, and this module is deleted.
"""
import pandas as pd

DISTRICTS = ("Arlington", "Jefferson", "Washington")

BASIS = ("derived from the office: the member was seated for this magisterial "
         "district, and a supervisor is assumed to have lived in the district "
         "he represented (residence-district); no record about the person")


def district_claims(members: pd.DataFrame) -> pd.DataFrame:
    """One claim per person per district they were seated for, dated to the
    start of the first term there. An at-large seat names no place."""
    seated = members[members.district.isin(DISTRICTS)]
    first = seated.sort_values(["start_year", "start_month"]).drop_duplicates(["name", "district"])
    return pd.DataFrame({
        "name": first.name, "year": first.start_year.astype(int).astype(str),
        "place": first.district + " District", "basis": BASIS,
        "source": "derived", "quote": "", "precision": "district"})
