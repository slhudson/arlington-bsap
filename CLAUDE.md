# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs the repository.

## The two stages

```
  |  code/fetch/        <- on demand: the network, output committed
data/raw/        published sources - a file here is its own citation
  |  code/transcribe/   <- on demand: OCR and reading, output committed
data/transcribed/  by_ocr/ and by_claude/ read off raw/
  |  code/build/        <- every subjective decision about what a number IS
data/clean/      built output
  |  code/analysis/     <- presentation only; cannot see anything above clean/
figures/         pdf/ for the paper, png/ for slides
  |
paper/           prose -> Overleaf -> compiled PDF
```

The four data layers are sorted by how the numbers were produced — published,
read by software, keyed in by a person, or computed here. Which folder
something belongs in depends on that, not on what it is about. Inside
`raw/`, folders are named for who published the material, not its subject.
`data/contents.csv` is the inventory: one row per file, with its layer, what
produced it, its source, what reads it, and for `raw/` a checksum;
`code/tests.py` refuses a file with no row and a raw file whose checksum has
moved.

**Build resolves ambiguity in the sources.** What a blank means, whether
categories overlap, which of two conflicting totals is right. If two reasonable
people could disagree about what the value *is*, the decision belongs in
`code/build/`.

**Analysis does arithmetic that is fully determined once those are settled.**
Dividing counts into shares, choosing a log axis, deciding which years to show.
Presentation choices are still subjective, but they cannot change a value. If
they would only disagree about how to *show* it, it belongs in `code/analysis/`.

This is enforced structurally, not by convention: `code/analysis/paths.py` has no
path to `data/raw/` or `data/transcribed/`. A figure script that wants to reach around the cleaning step
has nothing to reach with. Note that `analysis` scripts *append* `code/build/` to
`sys.path` rather than inserting it, so `code/build/paths.py` cannot shadow
`code/analysis/paths.py` and quietly restore that route.

## Naming

**A file is named after what it produces.** `code/clean/residents.py` writes
`data/clean/residents.csv`. `code/analysis/board_race.py` writes
`figures/pdf/board_race.pdf` and `figures/png/board_race.png`. No `make_`
prefixes, no `_chart` suffixes: the directory says what the stage does, the
filename says which thing. `run.sh` checks this after every figure, and warns
about figures in `figures/` that no step produces.

**Three subjects: `residents`, `voters` and `board`.** Everything is Arlington,
so nothing is prefixed `arlington_`.

**If you can run it, it lives with the code. If you can only read it, it lives
in `docs/`.** The reasoning behind a decision is in the subject's write-up
under `docs/`; the code carries a pointer to it, not an argument.

**`paths.py` is where real paths are assigned to the short names a stage
uses.** Fix the mapping once and every script in that stage follows. There is
one per stage, and that is deliberate — see above. They cannot be merged:
`code/build/paths.py` maps `data/raw/` and `code/analysis/paths.py` does not,
and that absence is the wall.

## The rules that matter

**`data/raw/` is read-only.** It is the files as published. Never edit,
rename, clean or "fix" anything inside it. A defect in a source is corrected
in `code/build/`, where the correction is visible and reviewable, never in the
file.

**Nothing reads `data/transcribed/`.** OCR misreads digits, so a number leaves
that folder the way it would without it: a person reads the scan and keys it
into `data/transcribed/by_claude/`, with a citation. The OCR shortens the
search; it does not do the reading.

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
departs from Urban, the departure and its reason are in `docs/figures.md`,
which holds the reasoning behind every visual convention; the style layer
states the values.

`style/` sits outside `code/` because most of it cannot be executed: a typeface
and a table of rcParams. `code/` is for things you can run.

**`run.sh` never touches the network.** Fetching a source is `code/fetch/`, run on
demand, which saves into `data/raw/` and commits the file. The build then
reads only what is committed.

Two reasons. Anyone who clones the repository can build it — no account, no API
key, no connection. And an API can change its answer, so a live call could move
a figure between runs with nothing in the repo to explain it; a committed file
is the same evidence standard as a scanned page.

The one exception is six census scans the build never reads, 50MB that
would push Overleaf past its ceiling. They are marked `in_git = no` in
`data/contents.csv` with their URL and checksum; `code/fetch/census_volumes.py`
fetches them and refuses a byte that differs, and `run.sh` says at the end of
every build if they are missing. A raw file the build reads is always
committed.

**Each code folder writes one data layer.** `code/fetch/` writes `data/raw/`,
`code/transcribe/` writes `data/transcribed/`, `code/build/` writes `data/clean/`,
`code/analysis/` writes `figures/`. `run.sh` runs the last two every time; the
first two run on demand — the network for one, a slow Mac-only OCR for the
other — and their output is committed, so the build is reproducible without
either. A script is named for what it produces: `code/fetch/elections.py`,
`code/transcribe/novack_terms.py`.

**`data/` holds what we take numbers out of.** A source consulted only to
settle a question — a boundary history, a news article, a methods note — is
cited in `paper/sources.bib` and filed in the project's Drive folder, not
downloaded into `data/raw/`.
The test is whether a figure derives from it.

**The Drive folder is filed by kind, and its index is generated.**
`code/archive.py` files the documents folder into `legal`, `reports`, `books`, `bios`,
`campaign websites`, `press`, `obituaries` and `census`, the kind being a rule on the
bib entry; writes `index.md` at its top from `paper/sources.bib` and
`data/contents.csv`, so the index cannot drift from either; and builds the
zip the County receives, the repository at HEAD with the six on-demand
scans and the folder. Without `--apply` it only reports. It refuses to act
while a name the bib says is filed is not in the folder, and deletes
nothing: a file no entry names goes to `unplaced/`.

**Every source column holds a citekey from `paper/sources.bib`.** One registry
for the prose and the data, so a footnote in the report and a cell in a table
name the same document. Entries are built from the document in hand, never from
memory; what is missing from the copy we hold goes in `annotation`, which
biblatex does not print. Three values are not citekeys - `assumed`,
`derived`, `unsourced` - and `code/citekeys.py` says what each one
admits to. Anything else stops the build.

**A row read from a census, a directory or a map states its match.** Those
records name a person, not a Board member; that the two are the same is a
decision. The `basis` column says what ties them - the name, the place,
an occupation or a spouse - and a name alone with nothing else in agreement
is no row.

**Guards that prevent silent wrongness get a test.** `code/tests.py` reintroduces
the specific mistake each guard exists to catch and asserts the build refuses,
so editing `code/build/` cannot quietly disable a check. `bash run.sh` runs it first;
it takes about five seconds.

Only silent failures are worth this. A figure script saving under the wrong
name halts the build with an error in your face; the Freedman village check
failing would show 4,596 in a figure and tell nobody.

**Fail loudly.** A script that cannot find its input, or whose numbers stop
tying out, should raise — not carry on and emit a plausible-looking figure with
wrong values. `code/clean/residents.py` asserts its derived columns still agree with
the figures they derive from, and `run.sh` fails if a script does not write the
figure it is named for.

**Both authors edit this code.** Write it to be read by someone else.

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes
bash run.sh               # build, then every figure
bash run.sh residents_per # build, then only matching figures
```

Invoke through `bash`, not `./run.sh` — the reason is at the top of `run.sh`.
`code/fetch/` and `code/transcribe/` also need `pymupdf`; the OCR needs a Mac. Neither
is required to rebuild.

## Questions and decisions

One write-up per subject, and one tracker. `docs/residents.md`,
`docs/board.md` and `docs/voters.md` hold what is settled about each: what
each number is, what backs it, what is assumed where nothing does, and why,
in the present tense, ending with a list of what still rests on an
assumption. `paper/sources.bib` is the registry of sources, and each entry's
`annotation` holds the notes on it. `docs/questions.csv` is the tracker: one row per open item, with a
stable slug for an id, its kind, an owner, the figure or table it bites, the
question in a sentence, and what would settle it. Three kinds: `source`, a
document to find or read; `decision`, a choice about how a number is built
or shown; and `scope`, a proposal for analysis the report does not yet do,
such as comparing Arlington's Board to peer localities. A row is something
that would change a number, a citation or a figure's form, or add an
analysis, once answered; meeting logistics and what to bring to whom are not
tracked here.

Log a question at the moment it arises, not in your head or in chat: a row
in the tracker, and a sentence in the subject write-up where it bites. When
it is settled, write the answer into the write-up and delete the row. Neither
records how a decision was reached or what was tried on the way; git has
that.

**An open question that changes a value gets a named function**, in a module
of its own under `code/build/`, applied by name in each figure - so which
figure takes which position is greppable rather than buried. When the question
is settled the assumption moves into the relevant build step and the function
is deleted. None is in force.

## Repository decisions

**One repository, with `paper/` inside it.** Overleaf syncs a whole
repository and cannot be scoped to `paper/` and `figures/`, so it carries the
data too. Its limits are on the files it syncs, not on git history: a
recommended 100MB in all, and a hard 7MB on editable (text) files, past
which GitHub sync stops working. One repository was chosen because pushing
figures across a repository boundary would undercut the case that this setup
is simpler than emailing files. `run.sh` warns at 80MB and at 6MB of text, so
revisiting does not depend on anyone remembering. The scans the build never
reads are already fetched on demand rather than committed, and so is the
OCR of the census volumes (`data/transcribed/by_ocr/`, regenerated on a Mac by
`code/transcribe/census.py`), which took 1.8MB of the text cap. If the cap
trips again, the candidate is the state's 2MB election CSV.

**A job that depends on another waits for its tracker row, not its branch.**
A project is finished when its row leaves `docs/questions.csv` on `main`;
that is what settling a question means here, and it is the only signal a
second session can check. Branches are invisible until pushed and can be
renamed, so a gate on "has that branch merged" passes for the wrong reason.
Push a branch the moment it is created, so that others can see it exists.

**Each session works in its own worktree** (`git worktree list`). Two
sessions sharing one checkout once produced committed figures built against
uncommitted edits, so `figures/` no longer matched `data/clean/` beside it.
A session hook in `.claude/settings.json` reminds an agent that starts in the
main checkout to offer a worktree when others may be working, and to check the
branch name fits the task. It advises; it never blocks, since collaborators
may be new to Git.
The build itself is reproducible: the same sources in a fresh virtualenv give
byte-identical figures.

**Figure formatting is not pinned.** Rebuilt figures may differ from earlier
renders by a few pixels with a newer matplotlib. Regression checks target the
numbers, not the rendering.

## Updates to the project lead

A session that runs for a while reports to someone who is not watching it and
cannot read its tool calls. Every status message, at each batch and whenever
it stops, has the same four lines, in plain words and with numbers first:

```
Task: <what this session is for, in one sentence>
Progress: X of Y <units of the task> done (Z%), <n> stuck
Left: <the remaining steps in one sentence, no member names unless needed>
Time: about N minutes, or "waiting on you" first if you need the lead
```

The units are the ones the task is measured in: members read, rows written,
sheets checked. Never a search term, a page id or an internal step. If the
lead is needed (a sign-in, a click, a decision), say so at the top of the
message. Say where the work is saved (branch and last commit) so nothing
lives only in the session.

## Register

This repository is read by collaborators. Write about artifacts and open
questions, never about people's performance. Early work here was exploratory by
design.
