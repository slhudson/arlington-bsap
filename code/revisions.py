"""Which sections of the report a person has revised, and which are still a first draft.

    .venv/bin/python code/revisions.py     # each section file, its mark, a count

The first line of every section file under paper/ is a comment:

    % revised: none
    % revised: SH 7 October 2026
    % revised: SH 7 October 2026; AK 9 October 2026

A section is marked when a person has rewritten it; reading it does not count
(Sally, 7 October 2026). The wrapper's \\sectioninput reads that same line and
stamps it beside the section on the contents page, so the file is the one
place the status lives. Several revisers are separated by "; ".

The sections are the files the wrapper pulls in with \\sectioninput, so a new
section is listed here by listing it there. A copy of the report written to
paper/drafts/ on or after DRAFT_CUTOFF must have no section still marked none
(code/tests.py).
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
WRAPPER = "arlington-bsap.tex"
DRAFT_CUTOFF = date(2026, 10, 30)  # the milestone copy at which every section has been revised (Sally, 7 October 2026)

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
REVISION = rf"[A-Z]{{2,3}} \d{{1,2}} (?:{MONTHS}) \d{{4}}"
MARK = re.compile(rf"^% revised: (none|{REVISION}(?:; {REVISION})*)$")


def section_files(paper_dir=PAPER):
    """The section files, in the order the wrapper reads them."""
    live = [re.sub(r"(?<!\\)%.*", "", line)
            for line in (paper_dir / WRAPPER).read_text().split("\n")]
    return [paper_dir / (m.group(1) + ".tex")
            for m in re.finditer(r"\\sectioninput\{([^}]+)\}", "\n".join(live))]


def mark(path):
    """The text after "revised:" on the file's first line. Raises when the line
    is missing or malformed, so a section cannot go unmarked unnoticed."""
    lines = path.read_text().split("\n")
    m = MARK.match(lines[0]) if lines else None
    if not m:
        raise ValueError(f"{path.name}: the first line must be '% revised: none' or "
                         f"'% revised: SH 7 October 2026', not {lines[0]!r}")
    return m.group(1)


def unrevised(paper_dir=PAPER):
    return [p for p in section_files(paper_dir) if mark(p) == "none"]


def draft_copies(paper_dir=PAPER):
    """(date, path) for each dated copy in paper/drafts/."""
    out = []
    for p in sorted((paper_dir / "drafts").glob("*.pdf")):
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})$", p.stem)
        if not m:
            raise ValueError(f"{p.name}: a draft copy is named arlington-bsap-YYYY-MM-DD.pdf")
        out.append((date(*map(int, m.groups())), p))
    return out


def late_copies_with_unrevised_sections(paper_dir=PAPER):
    """Problems: a copy dated on or after the cutoff while a section reads none."""
    left = unrevised(paper_dir)
    return [f"{p.name} is dated on or after {DRAFT_CUTOFF:%-d %B %Y} but "
            f"{len(left)} section(s) still read 'revised: none': "
            + ", ".join(f.name for f in left)
            for d, p in draft_copies(paper_dir) if d >= DRAFT_CUTOFF and left]


def main():
    files = section_files()
    width = max(len(str(f.relative_to(PAPER))) for f in files)
    for f in files:
        print(f"  {str(f.relative_to(PAPER)):<{width}}  {mark(f)}")
    left = len(unrevised())
    print(f"\n{len(files) - left} revised, {left} draft, of {len(files)} sections")


if __name__ == "__main__":
    sys.exit(main())
