"""Southeastern bodies keyed from their own pages -> data/built/localities_southeastern_bodies.csv

One row per city or county the Richmond appendix does not carry: the
jurisdiction with its state, its kind, its voting seats, the citekey of the
page behind the count and a note on how the seats add up, every column as
keyed. Nothing is parsed or chosen here: code/clean/localities_southeastern.py
decides which bodies the peer set holds.
"""
from paths import BY_CLAUDE, source, write

BODIES = BY_CLAUDE / "southeastern_bodies.csv"


def build():
    return source(BODIES, dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "localities_southeastern_bodies")
