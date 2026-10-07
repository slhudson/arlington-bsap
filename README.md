# Arlington BSaP

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. National Civic League (prime), with Sally
Hudson (Ranked Choice Virginia) and Alex Keena (VCU).

**Joining?** `docs/setup.md` is written to be pasted into a Claude
conversation and walks through getting set up. Day to day: ask Claude Code
for the change, `bash run.sh <figure>` shows one figure in seconds, a full
`bash run.sh` before you commit, and commit and push on main.

**Start with `CLAUDE.md`.** It holds the working rules and explains the one
idea everything else follows: `code/build/` reshapes the sources without
deciding anything, `code/clean/` decides what a number *is*, `code/analysis/`
decides how it is *shown*, and no stage can reach around the one before it.

## The pipeline

```
code/fetch/       -> data/raw/          published sources, saved as published
code/transcribe/  -> data/transcribed/  read off the scans
code/build/       -> data/built/        the sources reshaped; every value kept
code/clean/       -> data/clean/        every decision about what a number is
code/analysis/    -> figures/           which numbers a figure shows
style/                             how they are shown: conventions, palette, font
paper/                             the prose and sources.bib, via Overleaf
```

`bash run.sh` runs `code/build/`, the tests, `code/clean/` and
`code/analysis/`. The first two folders run on demand and their output is
committed, so anyone can rebuild without a network connection, an API key,
or a Mac. `data/built/` is not committed: it rebuilds in seconds from the
layers above, and `data/clean/` is the layer worth pulling across people.

**A script is named for what it writes**, so the folder is the index and
there is no list to keep: `code/clean/residents.py` writes
`data/clean/residents.csv`, and `code/analysis/members_by_race.py` writes
`figures/pdf/members_by_race.pdf` and its `.png`. What a number *is* and what
backs it is in that subject's write-up under `docs/`, listed at the bottom of
this file; where a raw file came from is its row in `data/contents.csv`.

**Not every file in a stage folder is a step.** Half of `code/clean/` is
modules the steps import — the roster readers, the terms they are built on,
an office's contests — and so are `code/analysis/members.py` and
`code/analysis/localities.py`. `run.sh` lists the steps, in the order they
run, one array per stage; a step is the file with a `__main__` block, or in
`code/analysis/` the one that saves a figure. `code/tests.py` holds those two
readings to each other, so a step cannot go missing from the list and a
module cannot creep into it.

Each stage has a `paths.py` that maps its own data folders and no higher:
`code/clean/paths.py` has no route above `data/built/`,
`code/analysis/paths.py` none above `data/clean/`. `code/citekeys.py` is the
citekeys `paper/bib/sources.bib` defines, read by both data stages.
Outside the stages, `code/sources/archive.py` writes `sources/documents`'s
`index.md` and the zip the County receives.

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes shapely
bash run.sh
```

`bash run.sh residents_per` rebuilds only matching figures and skips the
tests. Either way, a stage whose inputs are unchanged since a cached run is
copied back instead of rerun (`code/cache.py`). Invoke through
`bash`, not `./run.sh` — `run.sh` says why at the top. `code/transcribe/` and
`code/fetch/` need `pymupdf` as well, `code/fetch/ipums.py` needs `ipumspy`, and the
OCR needs a Mac; none of it is needed to rebuild.

## Writing

Prose is written in Overleaf, in a project linked to `arlington-bsap-draft`,
a mirror `code/publish.py` keeps to exactly `paper/`, `figures/pdf/` and `style/fonts/` -
Overleaf syncs a whole repository and cannot be scoped to folders, so
those are everything the mirror holds. Of those, only
`paper/arlington-bsap.tex`, `paper/bib/sources.bib` and `figures/pdf/` matter for
compiling.

**Citations come from `paper/bib/sources.bib`**, which is also where the `source`
columns in `data/clean/` point. Cite with `\autocite[6]{oleary2010}`; the key
is the same one the data uses, so a claim in the prose and a cell in a table
name the same document. The bibliography is set up but dormant - the `.tex`
says how to turn it on once the first citation is written.

**Pull from GitHub before a writing session, push when you finish.** In
Overleaf the control is the **Integrations** tab in the icon rail down the
left side of the editor, then GitHub — not under the Menu.

To change a figure, edit its script in `code/analysis/` and re-run. Never paste plot
data into a `.tex` file; that makes a second copy of the numbers that will
silently go stale.

## Where things are written down

| File | What it holds |
|---|---|
| `CLAUDE.md` | Working rules; the build/clean/analysis split; naming |
| `data/contents.csv` | Every data folder and file, and where it came from |
| `docs/residents.md`, `docs/elections.md`, `docs/members.md`, `docs/candidates.md`, `docs/localities.md` | What each number is, what backs it, what is assumed, and why; one per population |
| `docs/questions.csv` | What is still open: one row per item with an owner, what it bites and what would settle it |
| `docs/setup.md` | Getting a machine set up to build; written for a collaborator joining |
| `docs/web_access.md` | The websites the sources come from: what each needs from this machine, and what it refuses |
| `paper/bib/sources.bib` | Every source, cited by key from both the prose and `data/clean/`; each entry's `annotation` says what the copy held supports and where it is filed |
| `sources/documents` | Copies of the sources no number is taken from, filed by kind, with an `index.md` that `code/sources/archive.py` writes |

Open questions are logged as they arise and answered in place, so the reasoning
survives alongside the fix.
