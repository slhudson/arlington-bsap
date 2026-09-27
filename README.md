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

| Script | Writes | Explained in |
|---|---|---|
| `code/fetch/census.py` | `data/raw/us_census_bureau/<year>/*.csv` | `data/contents.csv` |
| `code/fetch/elections.py` | `data/raw/va_dept_of_elections/county_board_2000-2026.csv.gz` | `data/contents.csv` |
| `code/fetch/president.py` | `data/raw/va_dept_of_elections/president_1924-2024.csv` | `data/contents.csv` |
| `code/fetch/registration.py` | `data/raw/va_dept_of_elections/registration_2010-2025.csv` | `data/contents.csv` |
| `code/fetch/census_volumes.py` | `data/raw/us_census_bureau/<year>/<volume>-01.pdf` | `data/contents.csv` |
| `code/transcribe/census.py` | `data/transcribed/by_ocr/us_census_bureau/<year>/*.txt` | `data/contents.csv` |
| `code/transcribe/members_1870_1920.py` | `data/transcribed/by_claude/arlington_county/members_1870-1920.csv` | `data/contents.csv` |
| `code/transcribe/president_1872_1920.py` | `data/transcribed/by_claude/arlington_county/president_1872-1920.csv` | `data/contents.csv` |
| `code/transcribe/candidate_history.py` | `data/transcribed/by_claude/arlington_county/candidate_history_1920-present.csv` | `data/contents.csv` |
| `code/transcribe/novack_terms.py` | `data/transcribed/by_claude/arlington_historical_magazine/novack_terms_1930-1994.csv` | `data/contents.csv` |
| `code/build/elections.py` | `data/built/elections.csv` | its own docstring |
| `code/build/members_claims.py` | `data/built/members_claims.csv` | `docs/members.md` |
| `code/build/census.py` | `data/built/census.csv` | its own docstring |
| `code/build/registration.py` | `data/built/registration.csv` | its own docstring |
| `code/clean/residents.py` | `data/clean/residents.csv` | `docs/residents.md` |
| `code/clean/voters.py` | `data/clean/voters.csv` | `docs/voters.md` |
| `code/clean/members.py` | `data/clean/members.csv` | `docs/members.md` |
| `code/clean/members_residence.py` | `data/clean/members_residence.csv` | `docs/members.md` |
| `code/clean/members_by_year.py` | `data/clean/members_by_year.csv` | `docs/members.md` |
| `code/clean/voters_turnout.py` | `data/clean/voters_turnout.csv` | `docs/voters.md` |
| `code/analysis/<figure>.py` | `figures/pdf/<figure>.pdf`, `figures/png/<figure>.png` | its own docstring |
| `code/archive.py` | `index.md` at the top of the Drive documents folder, and the zip the County receives | `CLAUDE.md` |

Clean modules that write nothing, read by the steps above:
`code/clean/members_roster.py` (who held each seat and when, assembled from
one module per source, `members_roster_oleary.py`, `members_roster_novack.py`
and `members_roster_results.py`, on the terms `members_terms.py` defines),
`code/clean/elections.py` (an office's contests, selected from the built
table), `code/clean/census.py` (a census table in its own shape, from the
built cells) and `code/clean/members_census.py` (the census rows of the built
claims, coded), and one analysis module, `code/analysis/members.py` (who
sits on the Board in a year), is read by the Board figures.
`code/citekeys.py` (the citekeys `paper/sources.bib` defines) is read by
both data stages. Each stage has a `paths.py` that maps
its data folders, and `code/clean/paths.py` maps nothing above `data/built/`.

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes
bash run.sh
```

`bash run.sh residents_per` rebuilds only matching figures, skips the tests,
and reruns the data stages only if their inputs changed. Invoke through
`bash`, not `./run.sh` — `run.sh` says why at the top. `code/transcribe/` and
`code/fetch/` need `pymupdf` as well, `code/fetch/ipums.py` needs `ipumspy`, and the
OCR needs a Mac; none of it is needed to rebuild.

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
| `CLAUDE.md` | Working rules; the build/clean/analysis split; naming |
| `data/contents.csv` | Every data folder and file, and where it came from |
| `docs/residents.md`, `docs/voters.md`, `docs/members.md`, `docs/candidates.md`, `docs/localities.md` | What each number is, what backs it, what is assumed, and why; one per population |
| `docs/questions.csv` | What is still open: one row per item with an owner, what it bites and what would settle it |
| `docs/setup.md` | Getting a machine set up to build; written for a collaborator joining |
| `docs/web_access.md` | The websites the sources come from: what each needs from this machine, and what it refuses |
| `paper/sources.bib` | Every source, cited by key from both the prose and `data/clean/`; each entry's `annotation` says what the copy held supports and where it is filed |
| Drive, `sources/documents` | Copies of the sources no number is taken from, filed by kind, with an `index.md` that `code/archive.py` writes: <https://drive.google.com/drive/folders/10SGuURB-ldC1AzM3ClsdL_tAiWeFIZB4> |

Open questions are logged as they arise and answered in place, so the reasoning
survives alongside the fix.
