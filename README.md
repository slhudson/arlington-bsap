# Arlington BSaP

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. National Civic League (prime), with Sally
Hudson (Ranked Choice Virginia) and Alex Keena (VCU).

**Start with `CLAUDE.md`.** It holds the working rules and explains the one
idea everything else follows: `code/build/` decides what a number *is*, `code/analysis/`
decides how it is *shown*, and the second cannot reach around the first.

## The pipeline

```
code/fetch/       -> data/raw/          published sources, saved as published
code/transcribe/  -> data/transcribed/  read off the scans; by_human/ is hand-keyed
code/build/       -> data/clean/        every decision about what a number is
code/analysis/    -> figures/           how a number is shown; pdf/ and png/
paper/                             the prose and sources.bib, via Overleaf
```

`bash run.sh` runs the tests, then `code/build/`, then `code/analysis/`. The first two
folders run on demand and their output is committed, so anyone can rebuild
without a network connection, an API key, or a Mac.

| Script | Writes | Explained in |
|---|---|---|
| `code/fetch/census.py` | `data/raw/us_census_bureau/<year>/*.csv` | `data/contents.md` |
| `code/fetch/elections.py` | `data/raw/va_dept_of_elections/county_board_2021-2026.csv` | `data/contents.md` |
| `code/transcribe/census.py` | `data/transcribed/by_ocr/us_census_bureau/<year>/*.txt` | `data/contents.md` |
| `code/transcribe/board_1870_1920.py` | `data/transcribed/by_claude/arlington_county/board_1870-1920.csv` | `data/contents.md` |
| `code/transcribe/candidate_history.py` | `data/transcribed/by_claude/arlington_county/candidate_history_1920-present.csv` | `data/contents.md` |
| `code/transcribe/novack_terms.py` | `data/transcribed/by_claude/arlington_historical_magazine/novack_terms_1930-1994.csv` | `data/contents.md` |
| `code/build/residents.py` | `data/clean/residents.csv` | `docs/sources.md` — population |
| `code/build/board_members.py` | `data/clean/board_members.csv` | `docs/sources.md` — the roster, race and gender |
| `code/build/board_seats.py` | `data/clean/board_seats.csv` | `docs/sources.md` — seat-years |
| `code/analysis/<figure>.py` | `figures/pdf/<figure>.pdf`, `figures/png/<figure>.png` | `docs/figures.md` |

Five figures build. Two are in the paper so far, `residents_by_race` and
`board_race`; the rest are built and waiting on the outline.

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl
bash run.sh
```

`bash run.sh residents_per` rebuilds only matching figures. Invoke through
`bash`, not `./run.sh` — `run.sh` says why at the top. `code/transcribe/` and
`code/fetch/` need `pymupdf` as well, and the OCR needs a Mac; neither is needed to
rebuild.

## Writing

Prose is written in Overleaf, in the project linked to this repository.
Overleaf syncs the whole repo; only `paper/arlington-bsap.tex`,
`paper/sources.bib` and `figures/pdf/` matter for compiling.

**Citations come from `paper/sources.bib`**, which is also where the `source`
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
| `CLAUDE.md` | Working rules; the code/build/analysis split; naming |
| `data/contents.md` | Every data folder and file: where it came from, what reads it |
| `docs/sources.md` | What backs every number — geography, census, the roster, race and gender |
| `docs/questions.md` | Open methods questions, each with an owner; answered in place |
| `docs/figures.md` | Why each figure takes the form it does |
| `docs/setup.md` | Getting a machine set up to build; written for a collaborator joining |
| `paper/sources.bib` | Every source, cited by key from both the prose and `data/clean/` |

Open questions are logged as they arise and answered in place, so the reasoning
survives alongside the fix.
