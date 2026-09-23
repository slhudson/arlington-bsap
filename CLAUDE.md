# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs the repository.

## The two stages

```
  |  fetch/        <- on demand: the network, output committed
data/raw/        published sources - a file here is its own citation
  |  transcribe/   <- on demand: OCR and reading, output committed
data/transcribed/  by_ocr/ and by_claude/ read off raw/; by_human/ hand-keyed
  |  build/        <- every subjective decision about what a number IS
data/clean/      built output
  |  analysis/     <- presentation only; cannot see anything above clean/
figures/         pdf/ for the paper, png/ for slides
  |
paper/           prose -> Overleaf -> compiled PDF
```

The four data layers are sorted by how the numbers were produced — published,
read by software, keyed in by a person, or computed here. Which folder
something belongs in depends on that, not on what it is about. See
`data/contents.md`.

**Build resolves ambiguity in the sources.** What a blank means, whether
categories overlap, which of two conflicting totals is right. If two reasonable
people could disagree about what the value *is*, the decision belongs in
`build/`.

**Analysis does arithmetic that is fully determined once those are settled.**
Dividing counts into shares, choosing a log axis, deciding which years to show.
Presentation choices are still subjective, but they cannot change a value. If
they would only disagree about how to *show* it, it belongs in `analysis/`.

This is enforced structurally, not by convention: `analysis/files.py` has no
path to `data/raw/`, `data/transcribed/by_human/` or `data/transcribed/`. A figure script that wants to reach around the cleaning step
has nothing to reach with. Note that `analysis` scripts *append* `build/` to
`sys.path` rather than inserting it, so `build/files.py` cannot shadow
`analysis/files.py` and quietly restore that route.

## Naming

**A file is named after what it produces.** `build/residents.py` writes
`data/residents.csv`. `analysis/board_seats.py` writes
`figures/pdf/board_seats.pdf` and `figures/png/board_seats.png`. No `make_`
prefixes, no `_chart` suffixes: the directory says what the stage does, the
filename says which thing. `run.sh` checks this after every figure, and warns
about figures in `figures/` that no step produces.

**Two subjects: `residents` and `board`.** Everything is Arlington, so nothing
is prefixed `arlington_`.

**If you can run it, it lives with the code. If you can only read it, it lives
in `docs/`.** `build/assumptions.py` holds the mechanism of the two open
questions; the reasoning is in `docs/questions.md`. Code files carry a pointer,
not an argument.

**`files.py` is where real filenames are assigned to the short names the code
uses.** Fix the mapping once and every script follows. There is one per stage,
and that is deliberate — see above.

## The rules that matter

**`data/raw/` and `data/transcribed/by_human/` are read-only.** They are the files as
received. Never edit, rename, clean or "fix" anything inside them — including
the spacing in the `aapi_m embers` header, which is corrected in
`build/board_seats.py`.

**Nothing reads `data/transcribed/`.** OCR misreads digits, so a number leaves
that folder the way it would without it: a person reads the scan and keys it
into `data/transcribed/by_human/`, with a citation. The OCR shortens the search; it does not
do the reading.

**Everything is built by `bash run.sh`.** One entry point, no exceptions. If a
figure cannot be produced by running that from a clean checkout, it is not
finished.

**Never hand-edit `data/clean/` or `figures/`.** Both are generated and the
next run overwrites them. A change you want to keep is a change to a script.

**`data/clean/` is committed even though it is generated.** The usual rule is the
opposite, and we follow it elsewhere. These are small CSVs, and committing them
means a cleaning decision shows up as a reviewable diff — you can see exactly
which numbers moved and by how much. That matters while those are open.

**Visual conventions live in `analysis/style.py`.** Colors, fonts and figure
dimensions are imported, never redeclared, so a palette change is one edit.

**`run.sh` never touches the network.** Fetching a source is `fetch/`, run on
demand, which saves into `data/raw/` and commits the file. The build then
reads only what is committed.

Two reasons. Anyone who clones the repository can build it — no account, no API
key, no connection. And an API can change its answer, so a live call could move
a figure between runs with nothing in the repo to explain it; a committed file
is the same evidence standard as a scanned page.

**Each code folder writes one data layer.** `fetch/` writes `data/raw/`,
`transcribe/` writes `data/transcribed/`, `build/` writes `data/clean/`,
`analysis/` writes `figures/`. `run.sh` runs the last two every time; the
first two run on demand — the network for one, a slow Mac-only OCR for the
other — and their output is committed, so the build is reproducible without
either. A script is named for what it produces: `fetch/elections.py`,
`transcribe/novack_terms.py`.

**`data/` holds what we take numbers out of.** A source consulted only to
settle a question — a boundary history, a news article, a methods note — is
cited under Works cited in `docs/sources.md`, not downloaded into `data/raw/`.
The test is whether a figure derives from it.

**Guards that prevent silent wrongness get a test.** `tests.py` reintroduces
the specific mistake each guard exists to catch and asserts the build refuses,
so editing `build/` cannot quietly disable a check. `bash run.sh` runs it first;
it takes under a second.

Only silent failures are worth this. A figure script saving under the wrong
name halts the build with an error in your face; the Freedman village check
failing would show 4,596 in a figure and tell nobody.

**Fail loudly.** A script that cannot find its input, or whose numbers stop
tying out, should raise — not carry on and emit a plausible-looking figure with
wrong values. `build/residents.py` asserts its derived columns still agree with
the figures they derive from, and `run.sh` fails if a script does not write the
figure it is named for.

**Both authors edit this code.** Write it to be read by someone else.

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl
bash run.sh               # build, then every figure
bash run.sh residents_per # build, then only matching figures
```

Invoke through `bash`, not `./run.sh` — the reason is at the top of `run.sh`.
`fetch/` and `transcribe/` also need `pymupdf`; the OCR needs a Mac. Neither
is required to rebuild.

## Open questions

Questions that come up while working the files go in `docs/questions.md` at the
moment they arise, with an owner — not carried in your head or in chat. When
one is answered, write the answer into the file, not just the fix into the
code.

Two are currently unresolved and deliberately **not** settled in `build/`: the
1970/1990 category overlap, and whether not-reported reads as zero. Both are
in docs/questions.md.
Both live in `build/assumptions.py`, applied by name in each figure, so the
current disagreement between figures is greppable rather than buried. When they
are settled, the assumption moves into the relevant build step and the function
is deleted.

## Register

This repository is read by collaborators. Write about artifacts and open
questions, never about people's performance. Early work here was exploratory by
design.
