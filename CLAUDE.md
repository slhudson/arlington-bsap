# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs the repository.

## The three stages

```
  |  code/fetch/        <- on demand: the network, output committed
data/raw/        published sources - a file here is its own citation
  |  code/transcribe/   <- on demand: OCR and reading, output committed
data/transcribed/  by_ocr/ and by_claude/ read off raw/
  |  code/build/        <- reshaping only; every value that goes in comes out
data/built/      the sources in one shape each, not committed
  |  code/clean/        <- every subjective decision about what a number IS
data/clean/      the tables the figures read; committed
  |  code/analysis/     <- presentation only; cannot see anything above clean/
figures/         pdf/ for the paper, png/ for slides
  |
paper/           prose -> Overleaf -> compiled PDF
```

The five data layers are sorted by how the numbers were produced — published,
read by software, keyed in by a person, reshaped, or decided here. Which
folder something belongs in depends on that, not on what it is about. Inside
`raw/`, folders are named for who published the material, not its subject.
`data/contents.csv` is the inventory: one row per file, with its layer, its
source, and for `raw/` a checksum;
`code/tests.py` refuses a file with no row and a raw file whose checksum has
moved.

**Build reshapes and never decides.** Stacking the claim files into one table,
putting both election records in one, pulling Arlington's row out of a census
file, expanding a term into months. Every distinct value that goes in comes
out: `code/build/paths.py` compares each column an output shares with its
inputs and refuses the step if a value is missing. A build step that has to
choose is in the wrong stage.

**Clean resolves ambiguity in the sources.** What a blank means, whether
categories overlap, which of two conflicting totals is right, whether the
census line naming "E. Duncan" is the Board's Edward Duncan. If two reasonable
people could disagree about what the value *is*, the decision belongs in
`code/clean/`, and its output is exactly what a reviewer reads as a diff.

**Analysis does arithmetic that is fully determined once those are settled.**
Dividing counts into shares, choosing a log axis, deciding which years to show,
reading two grades of knowledge as one shade while `data/clean/` keeps them
apart. Presentation choices are still subjective, but they cannot change a
value. If they would only disagree about how to *show* it, it belongs in
`code/analysis/`.

This is enforced structurally, not by convention. `code/clean/paths.py` has no
path to `data/raw/` or `data/transcribed/`, and `code/analysis/paths.py` has
none to `data/built/` either: a script that wants to reach around the stage
before it has nothing to reach with. `code/tests.py` checks both.

## Naming

**A file is named after what it produces.** `code/clean/residents.py` writes
`data/clean/residents.csv`. `code/analysis/members_by_race.py` writes
`figures/pdf/members_by_race.pdf` and `figures/png/members_by_race.png`. No `make_`
prefixes, no `_chart` suffixes: the directory says what the stage does, the
filename says which thing. `run.sh` checks this after every figure, and warns
about figures in `figures/` that no step produces.

**A name's first word is the subject the file is about; the rest says how that
subject is cut or what about it is measured.** There are five: `residents`, the
county's people; `elections`, the contests they vote in; `members`, the people
who have served on the Board; `candidates`, the people who have run for it; and
`localities`, the Virginia jurisdictions Arlington is set against. Then
`residents_by_district`, `members_by_race`, `elections_turnout`,
`localities_density`. A subject is whatever a file is about, so people, places
and events all qualify; nothing is gained by forcing them into one word. Everything here is Arlington and everything is about the
Board, so nothing is prefixed `arlington_` and nothing is prefixed `board_`.

**The rows are the test of the first word, not its definition.**
`residents.csv` is one row per census year with residents in the columns, and
`members_by_year.csv` is one row per year with members in them; neither holds
a row per person, and both are named for the subject they count. What the
test catches is a file whose rows are a subject its name does not mention.
A table of peer localities is `localities`, because no row in it is a member, a
seat or a year of Arlington's Board. And a table of votes by contest is
`elections_results` rather than `voters`: what it counts is votes, and a voter
appears in it once per contest.

**`_by_` means grouped and counted.** `residents_by_age`, `members_by_race`:
the subject is sorted into categories and the figure shows how many are in
each. A bare attribute means the attribute shown per individual, ungrouped, so
`members_age` is a Lexis diagram with one diagonal per member and
`localities_density` is one dot per locality. Both say what the figure is
about; only the first says it is a breakdown.

**Three suffixes are not attributes.** `_by_year` and `_by_district` mark an
aggregate cut of a subject whose detail is the bare name. `_coverage` marks
how much of something is known rather than what it is:
`members_residence_coverage` shows how many members have a residence, not
where they lived. And where a third word names a source it reads
`members_roster_novack` — the subject, the thing, then who published it.

**If you can run it, it lives with the code. If you can only read it, it lives
in `docs/`.** The reasoning behind a decision is in the subject's write-up
under `docs/`; the code carries a pointer to it, not an argument.

**`paths.py` is where real paths are assigned to the short names a stage
uses.** Fix the mapping once and every script in that stage follows. There is
one per stage, and that is deliberate — see above. They cannot be merged:
`code/build/paths.py` maps `data/raw/`, `code/clean/paths.py` maps
`data/built/` and no higher, `code/analysis/paths.py` maps `data/clean/` and
no higher, and each absence is a wall.

## The rules that matter

**`data/raw/` is read-only.** It is the files as published. Never edit,
rename, clean or "fix" anything inside it. A defect in a source is corrected
in `code/clean/`, where the correction is visible and reviewable, never in the
file.

**Nothing reads `data/transcribed/`.** OCR misreads digits, so a number leaves
that folder the way it would without it: a person reads the scan and keys it
into `data/transcribed/by_claude/`, with a citation. The OCR shortens the
search; it does not do the reading.

**Everything is built by `bash run.sh`.** One entry point, no exceptions. If a
figure cannot be produced by running that from a clean checkout, it is not
finished. While editing one figure, `bash run.sh <figure>` rebuilds only it, in
seconds; the full run is for once before a commit.

**Never hand-edit `data/clean/` or `figures/`.** Both are generated and the
next run overwrites them. A change you want to keep is a change to a script.

**`data/clean/` is committed even though it is generated**, so a cleaning
decision shows up as a reviewable diff. `data/built/` is not: it holds no
decisions and `bash run.sh` makes it before anything reads it.
`docs/repository.md` has the reasoning.

**Visual conventions live in `style/`, not in `code/analysis/`.** Colors,
fonts, chart types and figure dimensions are imported, never redeclared, so a
palette change is one edit. `code/analysis/` holds the substance: which numbers
a figure shows and over what range.

The split is structural, like the one above it. `style/` has no `paths.py`,
so nothing in it has a route to `data/` at all — a chart helper that wanted to
reach a column has nothing to reach with. `run.sh` puts that folder on the path
for the analysis stage, so a figure script reads `import style` and
`import charts` and nothing else.

The conventions are the Urban Institute's, loaded from `style/urban.mplstyle`;
`docs/figures.md` holds the reasoning behind every visual convention and every
departure from Urban. The `figures` skill has the rules for editing one.

**`run.sh` never touches the network.** Fetching a source is `code/fetch/`, run on
demand, which saves into `data/raw/` and commits the file. The build then
reads only what is committed.

A raw file the build reads is always committed; the census scans it never
reads are fetched on demand (`docs/repository.md`).

**Each code folder writes one data layer.** `code/fetch/` writes `data/raw/`,
`code/transcribe/` writes `data/transcribed/`, `code/build/` writes
`data/built/`, `code/clean/` writes `data/clean/`, `code/analysis/` writes
`figures/` and, from `code/analysis/body_text_numbers.py`, the numbers the
prose cites that no figure carries, as LaTeX commands in
`paper/body_text_numbers.tex`. `run.sh` runs the last three every time; the
first two run on demand — the network for one, a slow Mac-only OCR for the
other — and their
output is committed, so the build is reproducible without either. A script is
named for what it produces: `code/fetch/elections.py`,
`code/transcribe/novack_terms.py`, `code/build/census.py`.

**`data/` holds what we take numbers out of.** A source consulted only to
settle a question — a boundary history, a news article, a methods note — is
cited in `paper/sources.bib` and filed in the project's Drive folder, not
downloaded into `data/raw/`.
The test is whether a figure derives from it. The `sources` skill has the
tools for fetching, citing and filing one.

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
so editing `code/build/` or `code/clean/` cannot quietly disable a check.
`bash run.sh` runs it after the build stage on a full run, about ten seconds;
a filtered run (`bash run.sh <figure>`) is for the figures and skips it.

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
bash run.sh               # build, test, then every figure
bash run.sh residents_per # only matching figures; build and clean only if their inputs changed, no tests
```

Invoke through `bash`, not `./run.sh` — the reason is at the top of `run.sh`.
`code/fetch/` and `code/transcribe/` also need `pymupdf`, and
`code/fetch/ipums.py` needs `ipumspy`; the OCR needs a Mac. None of it is
required to rebuild.

## Questions and decisions

One write-up per subject, and one tracker. `docs/residents.md`,
`docs/elections.md`, `docs/members.md`, `docs/candidates.md` and
`docs/localities.md` hold what is settled about each: what
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
tracked here. Nor is whether the report uses a figure that exists: the
figure is the reminder, so a `scope` row closes when its figure is built.

Log a question at the moment it arises, not in your head or in chat: a row
in the tracker, and a sentence in the subject write-up where it bites. When
it is settled, write the answer into the write-up and delete the row. Neither
records how a decision was reached or what was tried on the way; git has
that.

**An open question that changes a value gets a named function**, in a module
of its own under `code/clean/`, applied by name in each figure - so which
figure takes which position is greppable rather than buried. When the question
is settled the assumption moves into the relevant clean step and the function
is deleted. None is in force.

## Repository decisions

**One repository, with `paper/` inside it**, because Overleaf syncs a whole
repository. `run.sh` warns at 80MB in all and at 6MB of text, Overleaf's
limits; `docs/repository.md` says why one repository and what to move if a
warning fires.

**One session in a checkout works on main; two at once each take a
worktree on a branch** (`git worktree list`). Collaborators each work in
their own clone and meet only at push: a rejected push means pull, run the
build again, push. A session hook in `.claude/settings.json` says which case
applies at the start of every session, in plain words; it advises and never
blocks. A job that depends on another session's waits for its row to leave
`docs/questions.csv` on `main`, not for its branch. `docs/repository.md` has
the incident behind the rule and the reasoning.

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
