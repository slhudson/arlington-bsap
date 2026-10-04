"""How candidates were nominated, as the press says -> data/built/elections_nominations.csv

Passes data/transcribed/by_claude/elections_nominations.csv through unchanged;
nothing is reshaped. code/clean/elections_nominations.py joins it to the
primaries the county's history and the state's database print.
docs/elections.md, "How the Board's candidates were nominated".
"""
from paths import BY_CLAUDE, source, write


def build():
    return source(BY_CLAUDE / "elections_nominations.csv", dtype=str, keep_default_na=False)


if __name__ == "__main__":
    write(build(), "elections_nominations")
