# Arlington BSaP

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. National Civic League (prime), with Sally
Hudson (Ranked Choice Virginia) and Alex Keena (VCU).

## How this fits together

```
raw/         frozen source files, read-only
    |
    |   build/       cleaning: decides what each number IS
    v
data/        clean, analysis-ready CSVs
    |
    |   analysis/    figures: decides how a number is SHOWN
    v
figures/     generated PDFs and PNGs
    |
    |   \includegraphics, via \graphicspath
    v
paper/       main.tex - the prose
    |
    |   git push  ->  GitHub  ->  pull in Overleaf
    v
             compiled PDF
```

A number appears once, in a spreadsheet under `raw/`, and everything downstream
derives from it. Figure data is never retyped.

The split between the two stages is the important part. **`build/` is where
judgment goes** — what a blank means, whether census categories overlap, which
of two conflicting totals is right. **`analysis/` is deterministic given the
data** — it chooses how to show a number but cannot change one. That is
enforced rather than trusted: `analysis/paths.py` has no path to `raw/`.

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl
bash run.sh
```

`bash run.sh pct log` rebuilds only matching figures.

Use `bash run.sh` rather than `./run.sh`. Overleaf does not preserve Unix file
permissions, so any push from Overleaf strips the executable bit and
`./run.sh` then fails with "permission denied".

## Writing

Prose is written in Overleaf, in the project linked to this repository.
Overleaf syncs the whole repo, so the scans and scripts are visible there; only
`paper/main.tex` and `figures/` matter for compiling.

**Pull from GitHub before a writing session, push when you finish.** In
Overleaf the control is the **Integrations** tab in the narrow icon rail down
the left side of the editor, then GitHub — not under the Menu.

To change a figure, edit its script in `analysis/` and re-run. Never paste plot
data into a `.tex` file; that creates a second copy of the numbers that will
silently go stale.

## Where things are written down

| File | What it holds |
|---|---|
| `CLAUDE.md` | Working rules, the build/analysis split, known data issues |
| `docs/questions.md` | Open methods questions, each with an owner |
| `docs/sources.md` | What backs the race and gender coding; RA work order |
| `docs/figures.md` | Why each figure takes the form it does |

Open questions are logged as they arise and answered in place, so the reasoning
survives alongside the fix.
