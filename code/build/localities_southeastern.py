"""Southeastern cities of 180,000 to 300,000 residents, as Richmond's charter
review tabulates them -> data/built/localities_southeastern.csv

One row per city of Appendix E (richmond2023, printed p. 122), every column
as keyed: the city with its state, residents in thousands, form of
government, council members, how they are elected as printed ("7 Ward/3
at-large"), and the mayor's role. Nothing is parsed or chosen here:
code/clean/localities_southeastern.py decides what the council counts.
"""
from paths import BY_CLAUDE, source, write

CITIES = BY_CLAUDE / "city_of_richmond" / "southeastern_city_councils.csv"


def build():
    return source(CITIES, dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "localities_southeastern")
