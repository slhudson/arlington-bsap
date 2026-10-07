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
paper/                             the prose, in folders by part, and bib/sources.bib; Overleaf reads a mirror of it
```

`bash run.sh` runs `code/build/`, the tests, `code/clean/` and
`code/analysis/`. The first two folders run on demand and their output is
committed, so anyone can rebuild without a network connection, an API key,
or a Mac. `data/built/` is not committed: it rebuilds in seconds from the
layers above, and `data/clean/` is the layer worth pulling across people.

A script is named for what it writes, and each stage can reach only the one
before it; `CLAUDE.md` has the naming rules, which files in a stage folder are
steps, and the walls between stages. What a number *is* and what backs it is in
that subject's write-up under `docs/`; where a raw file came from is its row in
`data/contents.csv`.

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
those are everything the mirror holds. All of it matters for compiling: the
main file is `paper/arlington-bsap.tex`.

**Citations come from `paper/bib/sources.bib`**, which is also where the `source`
columns in `data/clean/` point. Cite with `\autocite[6]{oleary2010}`; the key
is the same one the data uses, so a claim in the prose and a cell in a table
name the same document.

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
| `docs/<subject>.md` (`residents`, `elections`, `members`, `candidates`, `localities`, `survey_satisfaction`, `survey_rcv`, `comments`) | What each number is, what backs it, what is assumed, and why; one per subject |
| `docs/questions.csv` | What is still open: one row per item with an owner, what it bites and what would settle it |
| `docs/setup.md` | Getting a machine set up to build; written for a collaborator joining |
| `docs/web_access.md` | The websites the sources come from: what each needs from this machine, and what it refuses |
| `paper/bib/sources.bib` | Every source, cited by key from both the prose and `data/clean/`; each entry's `annotation` says what the copy held supports and where it is filed |
| `sources/documents` | Copies of the sources no number is taken from, filed by kind, with an `index.md` that `code/sources/archive.py` writes |
