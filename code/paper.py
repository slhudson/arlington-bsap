"""Compile the report, and refuse a PDF that is quietly wrong.

    .venv/bin/python code/paper.py

Writes `paper/arlington-bsap.pdf`. Not part of `bash run.sh`: the figures
build with no LaTeX installed at all, and Overleaf compiles the report for
real. This is for compiling it locally without having to remember how.

Two things go wrong here, and only one of them announces itself.

Compiling with pdflatex stops dead, because the body text is set in Lato and
`fontspec` runs under no engine but lualatex or xelatex. That failure costs a
minute.

The other is silent. `latexmk` keeps a record of the tools it ran last time in
`paper/arlington-bsap.fdb_latexmk`. The report uses biblatex with
`backend=biber`; if that record holds bibtex from an earlier build, latexmk
goes on calling bibtex, which finds nothing to do in a biblatex document. The
PDF still builds. Every footnote citation and every cross-reference to a
figure comes out undefined, and a report with its sources missing looks
finished until somebody reads the footnotes.

So this script does not trust the exit code. It reads the log, and a log that
reports an undefined citation, an undefined reference or a substituted font is
a failed build however happily latexmk exited. Since a stale record is the
usual cause and clearing it is free, a first failure is retried once from
clean; only a failure that survives that is reported.

`docs/repository.md` has the reasoning, and `code/tests.py` reintroduces each
of these mistakes against `problems()` below.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
STEM = "arlington-bsap"

# Each pattern is a shape the log takes when the PDF is wrong but the build
# claimed to succeed. The message says what it means, because the log's own
# wording says only what LaTeX noticed, not what it costs.
SYMPTOMS = [
    (re.compile(r"Citation '([^']+)' .*? undefined"),
     "citation {0} did not resolve, so biber did not run: the bibliography "
     "and the footnote that cites it are missing"),
    (re.compile(r"Reference `([^']+)' .*? undefined"),
     "cross-reference to {0} did not resolve, so the text points at no figure"),
    (re.compile(r"Font shape `([^']+)' undefined"),
     "font {0} is missing, so that text is set in a substituted typeface; "
     "declare the face in \\setmainfont and put the file in style/fonts/"),
]


def problems(log):
    """Return what a compile log says is wrong, one sentence each.

    Pure: takes the log's text and returns strings. That is what makes this
    testable without a LaTeX installation, and it is why the checking lives
    here instead of inside the subprocess call below.
    """
    found = []
    for pattern, message in SYMPTOMS:
        # A single missing citation is reported on every pass, and one missing
        # font on every run of text that needed it, so report each name once.
        for name in dict.fromkeys(m.group(1) for m in pattern.finditer(log)):
            found.append(message.format(name))
    return found


def compile_once(clean):
    """Run latexmk, optionally clearing its record first. Returns the log."""
    if clean:
        subprocess.run(["latexmk", "-C"], cwd=PAPER,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["latexmk", "-pdflua", "-interaction=nonstopmode", f"{STEM}.tex"],
        cwd=PAPER, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = PAPER / f"{STEM}.log"
    return log.read_text(errors="replace") if log.exists() else ""


def main():
    if shutil.which("latexmk") is None:
        sys.exit("latexmk is not installed. The figures build without it "
                 "(bash run.sh); only the report needs it.")

    log = compile_once(clean=False)
    found = problems(log)
    if found:
        # A stale latexmk record is the usual cause and clearing it is free,
        # so spend the rebuild before believing the failure.
        print("first build looked wrong; clearing latexmk's record and "
              "rebuilding")
        log = compile_once(clean=True)
        found = problems(log)

    pdf = PAPER / f"{STEM}.pdf"
    if found:
        # Raise rather than leave a PDF that reads as finished.
        pdf.unlink(missing_ok=True)
        sys.exit("the report did not compile correctly:\n"
                 + "\n".join(f"  - {p}" for p in found)
                 + f"\n\nthe log is {pdf.with_suffix('.log')}, and "
                 "docs/repository.md explains both failures.")
    if not pdf.exists():
        sys.exit(f"latexmk wrote no {pdf.name}; see {pdf.with_suffix('.log')}")

    print(f"-> paper/{pdf.name} ({pdf.stat().st_size // 1024}KB), "
          "no undefined citations, references or fonts")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        STEM = sys.argv[1]          # e.g. "timelines", the other document in paper/
    main()
