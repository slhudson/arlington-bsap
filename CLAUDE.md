# Arlington BSaP — working rules

Historical and descriptive-representation analysis for Arlington County's Board
Structure and Performance study. Figures and the final PDF are built from this
repo; prose is written in Overleaf, which syncs a mirror of `paper/`.

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
filename says which thing. A figure script does not repeat its own name:
`paths.save(fig, profile)` takes the name from the running script, so saving
under another figure's name is not a thing that can be typed. `run.sh` still
checks that each step wrote its file, and warns about figures in `figures/`
that no step produces.

**Not every file in a stage folder is a step.** Half of `code/clean/` is
modules the steps import, and so are `code/analysis/members.py`,
`code/analysis/localities.py` and `code/analysis/elections.py`. `run.sh` lists the steps in the order they run,
one array per stage; a step is the file with a `__main__` block, or in
`code/analysis/` the one that calls `paths.save()`. `code/tests.py` holds the
two readings to each other, so a new step cannot be missing from run.sh and a
module cannot be listed as one.

**A name's first word is the subject the file is about; the rest says how that
subject is cut or what about it is measured.** There are six: `residents`, the
county's people; `elections`, the contests they vote in; `members`, the people
who have served on the Board; `candidates`, the people who have run for it;
`localities`, the Virginia jurisdictions Arlington is set against;
`survey`, the people a questionnaire reached, cut by which one -
`survey_satisfaction`, `survey_rcv`; and `comments`, the letters the Board
received. Then `residents_by_district`,
`members_by_race`, `elections_turnout`, `localities_peers`. A survey is its
own subject because its respondents are a sample and not the county: a share
of `residents` is every resident, a share of `survey_satisfaction` is every
resident who answered. A subject is whatever a file is about, so people, places
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
`localities_southeastern` is one dot per locality. Both say what the figure is
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
`figures/` and, from two steps that write LaTeX instead, what the paper
inputs: `code/analysis/body_text_numbers.py` writes the numbers the prose cites
that no figure carries as commands in `paper/body_text_numbers.tex`, and
`code/analysis/members_roster.py` writes the appendix roster's rows to
`paper/appendix/members_roster.tex`. `code/stage.py` runs the steps of `code/build/`, `code/clean/` and
`code/analysis/` in one process for `run.sh`;
it, `code/paper.py`, `code/merge.sh` and `code/merge_questions.py` (the
tracker's merge driver) sit outside the stages, like
`code/tests.py`: `code/paper.py` writes `paper/arlington-bsap.pdf` on demand, and
`code/merge.sh <branch>` brings a thread's branch into main once the build and
the compile pass on the merged tree (`docs/repository.md`).
`code/sources/` is outside them too, and writes no data layer: it holds the
tools that serve `paper/bib/sources.bib` and the copies filed under
`sources/documents` - fetching and
entering a source, filing the archive, cutting a web print back to its
article, checking a quotation against the copy it is attributed to. Only
`code/citekeys.py` sits loose at the top beside those two, because every stage
imports it. `run.sh` runs the last three every time; the
first two run on demand — the network for one, a slow Mac-only OCR for the
other — and their
output is committed, so the build is reproducible without either. A script is
named for what it produces: `code/fetch/elections.py`,
`code/transcribe/novack_terms.py`, `code/build/census.py`.

**`data/` holds what we take numbers out of.** A source consulted only to
settle a question — a boundary history, a news article, a methods note — is
cited in `paper/bib/sources.bib` and filed in `sources/documents`, committed in
the repository beside its citation rather than downloaded into `data/raw/`.
The test is whether a figure derives from it. The `sources` skill has the
tools for fetching, citing and filing one.

**Every source column holds a citekey from `paper/bib/sources.bib`.** One registry
for the prose and the data, so a footnote in the report and a cell in a table
name the same document. Entries are built from the document in hand, never from
memory; what is missing from the copy we hold goes in `annotation`, which
biblatex does not print. Three values are not citekeys - `assumed`,
`derived`, `unsourced` - and `code/citekeys.py` says what each one
admits to. Anything else stops the build.

**A quotation is checked against the copy it is attributed to.**
`code/sources/quotations.py` reads every entry `code/sources/archive.py` files under
`legal/` - the reporter scans and statute volumes, whose copies carry text -
and refuses one whose annotation quotes words the filed document does not
contain. Rose 1976 put a phrase in the Supreme Court of Appeals' mouth, the
report repeated it onto a slide the County was sent, and the opinion had been
in Drive the whole time. Not every quotation is the copy's own: a recorded
negative, another entry's words, a page the OCR did not reach. Each of those
is declared in that file with a reason a reader can check.

**A row read from a census, a directory or a map states its match.** Those
records name a person, not a Board member; that the two are the same is a
decision. The `basis` column says what ties them - the name, the place,
an occupation or a spouse - and a name alone with nothing else in agreement
is no row.

**Guards that prevent silent wrongness get a test.** `code/tests.py` reintroduces
the specific mistake each guard exists to catch and asserts the build refuses,
so editing `code/build/` or `code/clean/` cannot quietly disable a check.
`bash run.sh` runs it after the build stage on a full run, under a minute;
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
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl pyflakes shapely
bash run.sh               # build, test, then every figure
bash run.sh residents_per # only matching figures, no tests
```

Invoke through `bash`, not `./run.sh` — the reason is at the top of `run.sh`.
A stage whose inputs are the same bytes as a run already done in any
worktree of the clone is copied back from a cache in `.git` instead of
rerun, and so is a compile (`code/cache.py`, `docs/repository.md`).
`rm -rf "$(git rev-parse --git-common-dir)/build-cache"` empties it.
`code/fetch/` and `code/transcribe/` also need `pymupdf`, and
`code/fetch/ipums.py` needs `ipumspy`; the OCR needs a Mac. None of it is
required to rebuild.

**The paper compiles with lualatex, not pdflatex**, because its body text is
set in Lato. `run.sh` does not compile it; Overleaf does, and locally:

```bash
.venv/bin/python code/paper.py all   # writes paper/arlington-bsap.pdf and paper/timelines.pdf
```

That refuses a PDF whose log shows an undefined citation, cross-reference or
font, which latexmk itself passes. `docs/repository.md` has why, and the
Overleaf equivalent.

## Questions and decisions

One write-up per subject, and one tracker. `docs/residents.md`,
`docs/elections.md`, `docs/members.md`, `docs/candidates.md`,
`docs/localities.md`, `docs/survey_satisfaction.md` and `docs/comments.md`
hold what is settled
about each: what
each number is, what backs it, what is assumed where nothing does, and why,
in the present tense, ending with a list of what still rests on an
assumption. `paper/bib/sources.bib` is the registry of sources, and each entry's
`annotation` holds the notes on it. `docs/questions.csv` is the tracker: one row per open item, with a
stable slug for an id, its kind, whose court it waits in, the figure or table
it bites, the question in a sentence, what would settle it, and its
priority. Three kinds: `source`, a
document to find or read; `decision`, a choice about how a number is built
or shown; and `scope`, a proposal for analysis the report does not yet do,
such as comparing Arlington's Board to peer localities.

`priority` says what answering the row would do to the report, so a
co-author choosing what to chase reads it first. Three values: `high`, the
answer would change a figure or a claim the paper makes; `medium`, it would
add a sentence the paper does not yet have; `low`, it sharpens a footnote or
the bibliography and can wait for closeout. The ranking is Sally's; a blank
means she has not ranked the row, not that it is low. The `Physical` and
`Digital` rows were ranked on 7 October 2026: the county abstracts of votes
and the 1888 court order book at the Library of Virginia, the 1982 act
through a law-library login, and the Post's 1973 map of where officials
lived, are the four that would change the paper; the map is high because
residence is County-gated, and members placed from it are the case for the
County releasing its records (Sally, 7 October 2026).

`waiting_on` names who owes the next move, not who would do the work. Eight
courts: `Sally`; `Alex` for work Sally has offered him, which waits on his yes
until he takes it; `County` for anything the County meeting or its staff would
answer, which includes every figure on party or the presidential
vote and anything where County records may hold better data; `Claude` for
what a session can reach from here; `Physical` for a record that exists only
in an archive or a library and takes someone going there; `Digital` for what
sits behind a database login we do not have (HeinOnline, Westlaw, ProQuest);
`NCL` for what only the National Civic League can supply, which Sally asks for
when the drafting stage reaches it; and `closeout` for what cannot move until the end of the project. Who does a
Physical or Digital row is for Sally and Alex to settle; the court does not
say. An ask Sally makes whose answer is the County's waits on the County. How
the work gets done is in `settles`, so no column repeats it.

A row is something
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

**One repository, with `paper/` inside it**, so the paper and the figures
stay beside the data and the code that produced them, where the threads
work. Overleaf syncs a whole repository and cannot be scoped to folders,
so it is linked instead to a mirror, `arlington-bsap-draft`, which
`code/publish.py` push keeps to exactly `paper/`, `figures/pdf/` and `style/fonts/`; an edit
made in Overleaf comes back with `code/publish.py` pull, which
`code/merge.sh` runs as its first step and push as its last.
`docs/repository.md` says why two repositories and what the two commands do.

**One session in a checkout works on main; two at once each take a
worktree on a branch** (`git worktree list`). Collaborators each work in
their own clone and meet only at push: a rejected push means pull, run the
build again, push. A session hook in `.claude/settings.json` says which case
applies at the start of every session, in plain words. It advises and never
blocks, but `.githooks/pre-commit` does block: a commit in the primary checkout
is refused while more than one session is live there, because a broad `git add`
in a shared checkout commits whatever anyone else has in flight. Take a
worktree, or `git commit --no-verify` if you mean it. `run.sh` installs the
hook. A job that depends on another session's waits for its row to leave
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
message.

**The repository is not one of the four lines.** Branches, worktrees,
uncommitted files, which session is behind which, a merge, a conflict, a
rebase, a hook that refused a commit: the lead has delegated all of it, and
not because it does not matter. She holds that it matters and expects it done
carefully. She delegates it because a session can see the tree and she cannot,
so there is nothing she can add - "I rarely have anything to add on top of what
the agents can see and resolve themselves" (1 October 2026). Those are
different instructions: one would mean hiding the work, this one means doing it
without narrating it.

So commit and push before the status message rather than report where the work
is saved, and keep a commit hash on the sentence describing what changed, never
in a sentence about the repository's state. Taking the time is not the problem
and asking for it is not either - "a repository thing needs a few minutes" is a
better line than an unexplained gap. What is unwanted is the mechanics, and any
choice between git commands, which is ours to make.

The one thing worth her attention is plumbing that has stopped the work and
only she can unstop. Then one line saying what is blocked, in her terms.

Four things are not worth it, each handed to her on 6 October 2026 and
handed back. A failure that may be transient (a push refused, a key not
answering, a download that did not start) gets a second try, and a third
after a pause, before it is reported; "I don't understand why you can't
merge" was the answer to a key that worked on the next attempt. An
assumption she can rule on later is proceeded under, logged as a row, and
said in one line, not put to her as a question first; "are you able to
proceed under a reasonable assumption and flag it?" is her standing answer.
"Tell me when it's settled" and "say done when saved" are not sent: the
next message from her is the signal. And that the build, the tests and the
compile passed is never narrated; the merge proves it, and a failure is the
only news.

## Register

This repository is read by collaborators. Write about artifacts and open
questions, never about people's performance. Early work here was exploratory by
design.
