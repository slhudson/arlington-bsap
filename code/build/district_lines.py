"""data/transcribed/by_claude/district_lines.csv -> data/built/district_lines.csv

A pass-through: the transcribed vertices, unchanged. A build step either
way, so code/clean/residents_by_district_boundaries.py has only data/built/
to read (CLAUDE.md).
"""
import paths


def main():
    frame = paths.source(paths.BY_CLAUDE / "district_lines.csv")
    paths.write(frame, "district_lines")


if __name__ == "__main__":
    main()
