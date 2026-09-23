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
  needs a paid Claude plan; the $20-a-month one is enough.
- **Overleaf** is where the paper is written. It is linked to the GitHub
  repository, so the figures the scripts produce appear in the paper without
  being uploaded by hand.

## The repository

Everything is built by one command, `bash run.sh`, from files that are
committed in the repository. Data flows downward through four folders of
code, each writing one folder of data:

- `code/fetch/` downloads a published source and saves it, unchanged, into
  `data/raw/`. It is run only when a new source is needed; the downloaded
  file is committed, so nobody else needs to fetch it again.
- `code/transcribe/` reads the scanned documents in `data/raw/` into tables in
  `data/transcribed/`. Also run only when something new needs reading, and
  its output is committed. (`data/transcribed/by_human/` holds tables that
  were typed in by a person rather than read by a program.)
- `code/build/` turns the raw and transcribed files into the clean tables in
  `data/clean/`. This is where every decision about what a number *is* gets
  made — what a blank means, which of two conflicting figures to trust.
- `code/analysis/` draws the figures from `data/clean/` into `figures/`. One
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

1. **An invitation to the GitHub repository and to the Overleaf project.**
   Both are private, so someone already on them has to send the invitations
   — the repository's owner, or any collaborator with access. Cloning fails
   until the GitHub one is accepted, so this is the first thing to sort out.
2. **Git installed**, and signed in to GitHub.
3. **Claude Code installed and working.**
4. **Python with pandas, matplotlib and openpyxl**, in a virtual environment
   at `.venv` inside the repository folder:

       python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl

5. **A successful build.** `bash run.sh` from the repository folder should
   print the tests, a build step, five figures, and a line about
   `figures/pdf` and `figures/png`. That is the test that everything works.
   Invoke it through `bash`, not `./run.sh`; `run.sh` says why at the top.
6. **The Overleaf project open and synced.** In Overleaf, the GitHub link
   is under the **Integrations** tab in the icon rail down the left of the
   editor, not under the Menu; pull from GitHub before a writing session and
   push when done, so the paper and the repository stay the same thing.

## How to help

Any of these tools may be new to the person you're working with, or all of
them may already be in place; ask rather than assume, in either direction.
Where something is new, the setup is part of the job: installing Git and
signing in to GitHub, installing Claude Code and signing in to it, creating
the Python environment (which happens inside Claude Code once it is
running), cloning the repository, connecting to the Overleaf project, and
then getting oriented in it.

Start by asking whether they already have invitations to the GitHub
repository and the Overleaf project. If not, nothing else can proceed: tell
them to ask someone who is already on both — the repository's owner or any
existing collaborator — and say exactly what to ask for (an invitation to
the `slhudson/arlington-bsap` repository on GitHub, and to the
`arlington-bsap` project on Overleaf, both to the email address they'll use).

Then ask what operating system they're on, and go one step at a time: say what
to type, what they should see if it worked, and what to do if they see
something else, and wait for them to confirm before the next step. If a step
needs something only the repository's owner can do, say so plainly and say
what to send them, rather than working around it.

Once `bash run.sh` works, the setup is done. For orientation, a good first
thing to do is to open Claude Code inside the repository folder and ask it
to walk through `README.md` and `CLAUDE.md`; then change something small in
one figure — `code/analysis/` has one script per figure, named for the figure it
produces, and `code/analysis/style.py` holds the colours and fonts they share —
and rebuild, to see the loop work end to end.
