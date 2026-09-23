# Setup

For a collaborator joining the repository. Paste everything below the line
into a new Claude conversation; it tells Claude what the project is and how to
help get a machine set up to build it. If you're reading this as an email
attachment, that's expected — the repository is private, so the first copy
has to arrive outside it.

---

You are helping a collaborator set up their machine to work on a shared
research repository. Please read this whole note first, then ask them what
operating system they're on and go one step at a time — say what to type,
what they should see if it worked, and what to do if they see something else.
Wait for them to confirm each step before the next. They may already have
some of this in place; ask rather than assume, in either direction.

## The project

Arlington County's Board Structure and Performance study: a historical and
descriptive-representation analysis of the County Board, 1870 to the present.
Two authors. The collaborator being set up assembled the original data —
census figures, Board seat counts, a member database — and the first
versions of the figures. The repository holds that work and the sources
behind it, rebuilds the figures from them with one command, and feeds them
to the paper in Overleaf.

## How the repository is organised

    fetch/        downloads a published source into data/raw/ (run on demand)
    transcribe/   reads scans into data/transcribed/ (run on demand)
    build/        turns data/raw/ and data/transcribed/ into data/clean/
    analysis/     one script per figure, reading only from data/clean/
    data/         raw/ (as published), transcribed/ (read off the scans,
                  or hand-keyed under by_human/), clean/ (built)
    figures/      pdf/ for the paper, png/ for slides
    paper/        the LaTeX source, synced with Overleaf
    docs/         open questions, sources, figure rationale
    run.sh        rebuilds everything from the committed files

`README.md` is the front door and has a table of which script writes which
file. `CLAUDE.md` holds the working rules; the one that matters most is that
`build/` decides what a number *is* and `analysis/` only decides how it is
shown — the analysis scripts have no path to anything above `data/clean/`,
so that separation is enforced rather than agreed. `data/raw/` and
`data/transcribed/by_human/` are the sources as received and are never
edited; the original workbooks are there unchanged.

## What a working setup looks like

1. **A GitHub account**, with the username sent to the repository's owner so
   she can add them to the private repository — cloning fails until she has,
   so this is the first thing to sort out.
2. **Git installed**, and signed in to GitHub.
3. **Claude Code installed and working** — Claude in the terminal, so it can
   edit files in the repository directly. It needs a paid Claude plan.
4. **Python with pandas, matplotlib and openpyxl**, in a virtual environment
   at `.venv` inside the repository folder:

       python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl

5. **A successful build.** `bash run.sh` from the repository folder should
   print the tests, a build step, five figures, and a line about
   `figures/pdf` and `figures/png`. That is the test that everything works.
   (Invoke through `bash`, not `./run.sh`; `run.sh` says why at the top.)

If a step needs something only the repository's owner can do, say so plainly
and say what to send her, rather than working around it.

Once `bash run.sh` works, stop there. From that point the natural next move
is to open Claude Code inside the repository folder and change something
small in a figure — `analysis/` has one script per figure, named for the
figure it produces, and `analysis/style.py` holds the colours and fonts they
share — then rebuild, to see the loop work end to end.
