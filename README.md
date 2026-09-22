# Arlington BSaP

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. National Civic League (prime), with Sally
Hudson (Ranked Choice Virginia) and Alex Keena (VCU).

## How this fits together

```
raw/        frozen source files, read-only
   |
   |  ./run.sh
   v
figures/    generated PDFs and PNGs - never hand-edited
   |
   |  \includegraphics, via \graphicspath
   v
paper/      main.tex - the prose
   |
   |  git push  ->  GitHub  ->  pull in Overleaf
   v
            compiled PDF
```

Figure data is never retyped. A number appears once, in a spreadsheet under
`raw/`, and everything downstream derives from it.

## Rebuilding the figures

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl
./run.sh
```

`./run.sh pct log` rebuilds only matching scripts.

## Writing

Prose is written in Overleaf, in the project linked to this repository.
Overleaf syncs the whole repo, so the scans and scripts are visible there;
only `paper/main.tex` and `figures/` matter for compiling.

**Pull from GitHub before a writing session, push when you finish.** In
Overleaf the control is the Integrations tab in the left icon rail, then
GitHub - not under the Menu.

To change a figure, edit its script in `build/` and re-run. Never paste plot
data into a `.tex` file; that creates a second copy of the numbers that will
silently go stale.

## Where things are written down

| File | What it holds |
|---|---|
| `CLAUDE.md` | Working rules and known data issues |
| `questions.md` | Open methods questions, each with an owner |
| `sources.md` | What backs the race and gender coding; RA work order |
| `figures.md` | Why each figure takes the form it does |

Open questions are logged as they arise and answered in place, so the reasoning
survives alongside the fix.
