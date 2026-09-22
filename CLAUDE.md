# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs `paper/` and `figures/`.

## The rules that matter

**`raw/` is read-only.** It is a dated snapshot of the files as received. Never
edit, rename, clean or "fix" anything inside it — not even the `aapi_m embers`
header typo. Corrections belong downstream, in `build/`, where they are visible
as code.

**Everything is built by `./run.sh`.** One entry point, no exceptions. If a
figure cannot be produced by running that script from a clean checkout, it is
not finished.

**Never hand-edit anything in `figures/`.** It is generated output and the next
run will silently overwrite it. A change you want to keep is a change to a
script.

**Data transformations live in `build/`, not in plotting scripts.** A cleaning
decision — how 1970/1990 category overlap is reconciled, how not-reported is
distinguished from zero — is made once, in one place, and every figure inherits
it. The moment two scripts decide the same question differently, they can
disagree in print.

**Visual conventions live in the shared style module.** Colors, fonts and figure
dimensions are imported, never redeclared per script, so a palette change is a
single edit.

**Paths come from `build/paths.py`.** No absolute paths anywhere, so the repo
works on anyone's machine.

**Fail loudly.** A script that cannot find its input, or whose numbers stop
tying out, should raise — not carry on and emit a plausible-looking figure with
wrong values. Template-filling and find-and-replace are the usual offenders:
raise when the anchor is missing rather than silently no-op.

**Both authors edit the figure code.** Write it to be read by someone else.

## Layout

```
raw/2026-09-22-handoff/   frozen inputs, read-only
build/                    data prep, style module, figure scripts
figures/                  generated output — never hand-edited
paper/                    Overleaf-synced prose
run.sh                    rebuilds every figure from raw/
```

## Running it

```bash
./run.sh                  # rebuild all five figures
./run.sh pct log          # rebuild only matching scripts
```

Needs `.venv` (gitignored): `python3 -m venv .venv && .venv/bin/pip install
pandas matplotlib openpyxl`.

## Known data issues

Tracked in the handoff; unresolved ones are listed here so they are not
rediscovered. Do not silently pick a side on any of these.

- **1970 and 1990 race categories sum above the reported total** (~2.8% and
  ~0.2%). `_pct` rescales to 100%; the count chart plots as reported. They
  disagree. Must be settled in `build/` before figures go to the County.
- **Not-reported read as zero.** Hispanic is blank before 1970, AAPI before
  1950, because those categories were not separately tabulated. `fillna(0)`
  treats absence as zero; the log chart instead starts each line when first
  reported. A zero and an absence are different claims.
- **1883, 1884, 1931** are `"."` in the counts file and render as gaps.
- **Fractional seats** occur when a member resigned or died mid-year and was
  replaced. Figure note: "Half seats occur when a Board member resigned or died
  before the end of the year and was subsequently replaced."
- **The two board files cover different periods** — roster from 1932, counts
  from 1871. The 1871–1931 counts have no person-level backing.
- **1890 population is 4,596**, from the scanned volumes in `raw/`. An earlier
  estimate of 4,258 is superseded.

## Provenance

Descriptive coding sources are being collected in `PROVENANCE.md`. The
load-bearing open question is what supports "first Black member since
Reconstruction" — i.e. whether 1889–1986 was ever systematically reviewed.
