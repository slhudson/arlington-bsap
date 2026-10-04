"""The Alexandria Gazette's returns for supervisor, 1885-1919 -> data/built/candidates_gazette.csv

Passes data/transcribed/by_claude/candidates_gazette.csv through unchanged;
nothing is reshaped. code/clean/elections_margins.py reads it for the
single-seat district contests whose losers the Gazette names.
docs/candidates.md, "1870-1919, the Alexandria Gazette's returns".
"""
from paths import BY_CLAUDE, source, write


def build():
    return source(BY_CLAUDE / "candidates_gazette.csv", dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "candidates_gazette")
