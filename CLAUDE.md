# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs the repository.

## The two stages

```
  |  code/fetch/        <- on demand: the network, output committed
data/raw/        published sources - a file here is its own citation
  |  code/transcribe/   <- on demand: OCR and reading, output committed
data/transcribed/  by_ocr/ and by_claude/ read off raw/; by_human/ hand-keyed
  |  code/build/        <- every subjective decision about what a number IS
data/clean/      built output
  |  code/analysis/     <- presentation only; cannot see anything above clean/
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
`code/build/`.

**Analysis does arithmetic that is fully determined once those are settled.**
Dividing counts into shares, choosing a log axis, deciding which years to show.
Presentation choices are still subjective, but they cannot change a value. If
they would only disagree about how to *show* it, it belongs in `code/analysis/`.

This is enforced structurally, not by convention: `code/analysis/paths.py` has no
path to `data/raw/`, `data/transcribed/by_human/` or `data/transcribed/`. A figure script that wants to reach around the cleaning step
has nothing to reach with. Note that `analysis` scripts *append* `code/build/` to
`sys.path` rather than inserting it, so `code/build/paths.py` cannot shadow
`code/analysis/paths.py` and quietly restore that route.

## Naming

**A file is named after what it produces.** `code/build/residents.py` writes
`data/clean/residents.csv`. `code/analysis/board_race.py` writes
`figures/pdf/board_race.pdf` and `figures/png/board_race.png`. No `make_`
prefixes, no `_chart` suffixes: the directory says what the stage does, the
filename says which thing. `run.sh` checks this after every figure, and warns
about figures in `figures/` that no step produces.

**Three subjects: `residents`, `voters` and `board`.** Everything is Arlington,
so nothing is prefixed `arlington_`.

**If you can run it, it lives with the code. If you can only read it, it lives
in `docs/`.** The reasoning behind a decision is in `docs/questions.md`; the
code carries a pointer to it, not an argument.

**`paths.py` is where real paths are assigned to the short names a stage
uses.** Fix the mapping once and every script in that stage follows. There is
one per stage, and that is deliberate — see above. They cannot be merged:
`code/build/paths.py` maps `data/raw/` and `code/analysis/paths.py` does not,
and that absence is the wall.

## The rules that matter

**`data/raw/` and `data/transcribed/by_human/` are read-only.** They are the files as
received. Never edit, rename, clean or "fix" anything inside them — including
the spacing in the `aapi_m embers` header, which is corrected in
`code/build/board_seats.py`.

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

**Visual conventions live in `style/`, not in `code/analysis/`.** Colors,
fonts, chart types and figure dimensions are imported, never redeclared, so a
palette change is one edit. `code/analysis/` holds the substance: which numbers
a figure shows and over what range.

The split is structural, like the one above it. `style/` has no `paths.py`,
so nothing in it has a route to `data/` at all — a chart helper that wanted to
reach a column has nothing to reach with. `run.sh` puts that folder on the path
for the analysis stage, so a figure script reads `import style` and
`import charts` and nothing else.

The conventions themselves are the Urban Institute's data visualization style
guide, loaded from `style/urban.mplstyle` and cited there. Where this project
departs from Urban, the departure is in `style/style.py` with its reason.

`style/` sits outside `code/` because most of it cannot be executed: a typeface
and a table of rcParams. `code/` is for things you can run.

**`run.sh` never touches the network.** Fetching a source is `code/fetch/`, run on
demand, which saves into `data/raw/` and commits the file. The build then
reads only what is committed.

Two reasons. Anyone who clones the repository can build it — no account, no API
key, no connection. And an API can change its answer, so a live call could move
a figure between runs with nothing in the repo to explain it; a committed file
is the same evidence standard as a scanned page.

**Each code folder writes one data layer.** `code/fetch/` writes `data/raw/`,
`code/transcribe/` writes `data/transcribed/`, `code/build/` writes `data/clean/`,
`code/analysis/` writes `figures/`. `run.sh` runs the last two every time; the
first two run on demand — the network for one, a slow Mac-only OCR for the
other — and their output is committed, so the build is reproducible without
either. A script is named for what it produces: `code/fetch/elections.py`,
`code/transcribe/novack_terms.py`.

**`data/` holds what we take numbers out of.** A source consulted only to
settle a question — a boundary history, a news article, a methods note — is
cited under Works cited in `docs/sources.md`, not downloaded into `data/raw/`.
The test is whether a figure derives from it.

**Every source column holds a citekey from `paper/sources.bib`.** One registry
for the prose and the data, so a footnote in the report and a cell in a table
name the same document. Entries are built from the document in hand, never from
memory; what is missing from the copy we hold goes in `annotation`, which
biblatex does not print. Four values are not citekeys - `keena-workbook`,
`assumed`, `derived`, `unsourced` - and `code/build/citekeys.py` says what each one
admits to. Anything else stops the build.

**Guards that prevent silent wrongness get a test.** `code/tests.py` reintroduces
the specific mistake each guard exists to catch and asserts the build refuses,
so editing `code/build/` cannot quietly disable a check. `bash run.sh` runs it first;
it takes under a second.

Only silent failures are worth this. A figure script saving under the wrong
name halts the build with an error in your face; the Freedman village check
failing would show 4,596 in a figure and tell nobody.

**Fail loudly.** A script that cannot find its input, or whose numbers stop
tying out, should raise — not carry on and emit a plausible-looking figure with
wrong values. `code/build/residents.py` asserts its derived columns still agree with
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
`code/fetch/` and `code/transcribe/` also need `pymupdf`; the OCR needs a Mac. Neither
is required to rebuild.

## Open questions

Questions that come up while working the files go in `docs/questions.md` at the
moment they arise, with an owner — not carried in your head or in chat. When
one is answered, write the answer into the file, not just the fix into the
code.

**An open question that changes a value gets a named function**, in a module
of its own under `code/build/`, applied by name in each figure - so which
figure takes which position is greppable rather than buried. When the question
is settled the assumption moves into the relevant build step and the function
is deleted.

There are none in force. The two that were - the 1970/1990 category overlap
and whether not-reported reads as zero - are settled, and `assumptions.py`
went with them. The overlap turned out not to be an overlap: 1970's Hispanic
and Asian/Pacific Islander columns were transposed in the delivered workbook,
and the categories partition the county once they are read off the source.
Both are written up in `docs/questions.md`.

## Register

This repository is read by collaborators. Write about artifacts and open
questions, never about people's performance. Early work here was exploratory by
design.
