"""data/transcribed/by_claude/alexandria_annexation_1915.csv -> data/built/alexandria_annexation_1915.csv

A pass-through: the transcribed vertices, unchanged. A build step either
way, so code/clean/residents_by_district_boundaries.py has only data/built/
to read (CLAUDE.md).
"""
import paths


def main():
    frame = paths.source(paths.BY_CLAUDE / "alexandria_annexation_1915.csv")
    paths.write(frame, "alexandria_annexation_1915")


if __name__ == "__main__":
    main()
