# Setup

For anyone joining the repository. Paste everything below the line into a
new Claude conversation; it tells Claude what the project is and how to help
get a machine set up to build it.

---

## The project

Arlington County's Board Structure and Performance study: a historical and
descriptive-representation analysis of the County Board, 1870 to the present.
The work product is a paper with figures. The figures are drawn from data
that the repository assembles from primary sources — census volumes, the
county's election records, a published roster of Board members, and the
project's own workbooks — and every number in them can be traced back to the
page it came from.

## The tools

Four things, each doing one job:

- **Git and GitHub** keep the repository. It is private, on GitHub, and
  everyone works from their own copy on their own machine, pushing changes
  back when they are done.
- **Python** does the computing. The scripts need three packages — pandas,
  matplotlib and openpyxl — which live in a virtual environment inside the
  repository folder so nothing has to be installed system-wide.
- **Claude Code** is Claude in the terminal. It can read and edit the files
  in the repository directly, run the build, and explain what it finds. It
  needs a paid Claude plan.
- **Overleaf** is where the paper is written. It is linked to the GitHub
  repository, so the figures the scripts produce appear in the paper without
  being uploaded by hand.

## The repository

Everything is built by one command, `bash run.sh`, from files that are
committed in the repository. Data flows downward through four folders of
code, each writing one folder of data:

- `fetch/` downloads a published source and saves it, unchanged, into
  `data/raw/`. It is run only when a new source is needed; the downloaded
  file is committed, so nobody else needs to fetch it again.
- `transcribe/` reads the scanned documents in `data/raw/` into tables in
  `data/transcribed/`. Also run only when something new needs reading, and
  its output is committed. (`data/transcribed/by_human/` holds tables that
  were typed in by a person rather than read by a program.)
- `build/` turns the raw and transcribed files into the clean tables in
  `data/clean/`. This is where every decision about what a number *is* gets
  made — what a blank means, which of two conflicting figures to trust.
- `analysis/` draws the figures from `data/clean/` into `figures/`. One
  script per figure. These scripts decide how a number is shown, and they
  cannot see anything above `data/clean/`, so a figure can never quietly
  change a value.

`run.sh` runs the last two every time; the first two only run when someone
asks for them. Alongside those: `paper/` holds the LaTeX source that Overleaf
syncs, and `docs/` holds the open questions, the record of what backs every
number, and the reasoning behind each figure.

Two rules to know before touching anything. `data/raw/` and
`data/transcribed/by_human/` are the sources as received and are never
edited. And `README.md` is the front door — it has a table of which script
writes which file — while `CLAUDE.md` holds the working rules.

## What a working setup looks like

1. **A GitHub account**, with the username sent to the repository's owner so
   they can be added to the private repository — cloning fails until then,
   so this is the first thing to sort out.
2. **Git installed**, and signed in to GitHub.
3. **Claude Code installed and working.**
4. **Python with pandas, matplotlib and openpyxl**, in a virtual environment
   at `.venv` inside the repository folder:

       python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl

5. **A successful build.** `bash run.sh` from the repository folder should
   print the tests, a build step, five figures, and a line about
   `figures/pdf` and `figures/png`. That is the test that everything works.
   Invoke it through `bash`, not `./run.sh`; `run.sh` says why at the top.

## How to help

The person you're working with wants to get from wherever they are now to a
working setup. Ask what operating system they're on, then go one step at a
time: say what to type, what they should see if it worked, and what to do if
they see something else, and wait for them to confirm before the next step.
They may already have some of this in place; ask rather than assume, in
either direction.

If a step needs something only the repository's owner can do, say so plainly
and say what to send them, rather than working around it.

Once `bash run.sh` works, stop there. A good first thing to try afterwards is
to open Claude Code inside the repository folder, change something small in
one figure — `analysis/` has one script per figure, named for the figure it
produces, and `analysis/style.py` holds the colours and fonts they share —
and rebuild, to see the loop work end to end.
