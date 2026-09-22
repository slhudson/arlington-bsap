# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs the repository.

## The two stages

```
raw/        frozen sources, read-only
  |  build/     <- every subjective decision about what a number IS
data/       clean, analysis-ready
  |  analysis/  <- presentation only; cannot see raw/
figures/    generated output
  |
paper/      prose -> Overleaf -> compiled PDF
```

**Build resolves ambiguity in the sources.** What a blank means, whether
categories overlap, which of two conflicting totals is right. If two reasonable
people could disagree about what the value *is*, the decision belongs in
`build/`.

**Analysis does arithmetic that is fully determined once those are settled.**
Dividing counts into shares, choosing a log axis, deciding which years to show.
Presentation choices are still subjective, but they cannot change a value. If
they would only disagree about how to *show* it, it belongs in `analysis/`.

This is enforced structurally, not by convention: `analysis/paths.py` has no
path to `raw/`. A figure script that wants to reach around the cleaning step
has nothing to reach with. Note that `analysis` scripts *append* `build/` to
`sys.path` rather than inserting it, so `build/paths.py` cannot shadow
`analysis/paths.py` and quietly restore that route.

## The rules that matter

**`raw/` is read-only.** It is a dated snapshot of the files as received. Never
edit, rename, clean or "fix" anything inside it — including the spacing in the
`aapi_m embers` header, which is corrected in `build/clean.py`.

**Everything is built by `bash run.sh`.** One entry point, no exceptions. If a
figure cannot be produced by running that from a clean checkout, it is not
finished.

**Never hand-edit `data/` or `figures/`.** Both are generated and the next run
overwrites them. A change you want to keep is a change to a script.

**`data/` is committed even though it is generated.** The usual rule is the
opposite, and we follow it elsewhere. These are small CSVs, and committing them
means a cleaning decision shows up as a reviewable diff — you can see exactly
which numbers moved and by how much. That matters while Q1 and Q2 are open.

**Visual conventions live in `analysis/style.py`.** Colors, fonts and figure
dimensions are imported, never redeclared, so a palette change is one edit.

**Fail loudly.** A script that cannot find its input, or whose numbers stop
tying out, should raise — not carry on and emit a plausible-looking figure with
wrong values. `build/clean.py` asserts its derived columns still agree with the
figures they derive from.

**Both authors edit this code.** Write it to be read by someone else.

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl
bash run.sh               # build, then every figure
bash run.sh pct log       # build, then only matching figures
```

Invoke through `bash`, not `./run.sh`. Overleaf does not preserve Unix file
permissions, so a push from Overleaf strips the executable bit.

## Open questions

Questions that come up while working the files go in `docs/questions.md` at the
moment they arise, with an owner — not carried in your head or in chat. When
one is answered, write the answer into the file, not just the fix into the
code.

Two are currently unresolved and deliberately **not** settled in `build/`: the
1970/1990 category overlap (Q1) and whether not-reported reads as zero (Q2).
Both treatments live in `build/conventions.py`, applied explicitly by each
figure, so the current disagreement between figures is visible in code rather
than buried. When they are settled, the chosen treatment moves into
`build/clean.py` and the per-figure calls go away.

## Register

This repository is read by collaborators. Write about artifacts and open
questions, never about people's performance. Early work here was exploratory by
design.
