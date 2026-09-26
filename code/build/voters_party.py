"""Non-Democratic County Board candidates' party since 2023, as a press or
campaign source names it -> data/built/voters_party.csv

Passes data/transcribed/by_claude/voters_party.csv through unchanged; nothing
is reshaped. code/clean/voters.py reads it for a general-election candidate
the state record carries no party for. docs/voters.md, "For County Board".
"""
from paths import BY_CLAUDE, source, write


def build():
    return source(BY_CLAUDE / "voters_party.csv", dtype=str)


if __name__ == "__main__":
    write(build(), "voters_party")
