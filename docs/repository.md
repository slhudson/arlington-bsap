# Repository decisions

The reasoning behind the rules in `CLAUDE.md` about how the repository is
kept. `CLAUDE.md` states each rule and points here; this file says why, and
what happened where a rule came from an incident.

## Why `data/clean/` is committed and `data/built/` is not

**`data/clean/` is committed even though it is generated.** The usual rule is
the opposite, and this repository follows it everywhere else. These are small
CSVs, and committing them means a cleaning decision shows up as a reviewable
diff: a reader can see exactly which numbers moved and by how much. That matters while those are open.
`data/built/` is not committed: it holds no decisions, rebuilds in seconds
from the layers above.
`bash run.sh` makes it before anything reads it.

## Why the style layer sits outside `code/`

The conventions themselves are the Urban Institute's data visualization style
guide, loaded from `style/urban.mplstyle` and cited there. Where this project
departs from Urban, the departure and its reason are in `docs/figures.md`,
which holds the reasoning behind every visual convention; the style layer
states the values.

`style/` sits outside `code/` because most of it cannot be executed: a typeface
and a table of rcParams. `code/` is for things you can run.

## Why `run.sh` never touches the network

Two reasons. Anyone who clones the repository can build it — no account, no API
key, no connection. And an API can change its answer, so a live call could move
a figure between runs with nothing in the repo to explain it; a committed file
is the same evidence standard as a scanned page.

The one exception is the census volume scans the build never reads, bulk
nothing reads. They are marked `in_git = no` in
`data/contents.csv` with their URL and checksum; `code/fetch/census_volumes.py`
fetches them and refuses a byte that differs, and `run.sh` says at the end of
every build if they are missing. A published file the build reads is
always committed.

## The Overleaf mirror

Two repositories hold this project: the whole one, `arlington-bsap`, where
the five stages and the threads work, and a second, `slhudson/arlington-bsap-draft`,
which Overleaf is linked to and syncs nothing else. Overleaf syncs a whole
repository and has no way to scope that to two folders, and it can create a
GitHub repository but never link to an existing one - so the repository
Overleaf was already linked to keeps that link and plays the mirror, and a
newly created repository takes the whole project's name. `code/publish.py`
keeps the invariant between them: `push` rebuilds the mirror's tree as
exactly `paper/`, `figures/pdf/` and `style/fonts/` from this repository's `HEAD`, committed
on top of the mirror's own history rather than rewriting it, so Overleaf
keeps its common ancestor; `pull` reads the mirror's commits back to the last
one of ours - an edit made in Overleaf - and applies the changes under
`paper/` to a new branch, `overleaf-<date>`, ready for
`bash code/merge.sh overleaf-<date>`. The branch and its commit are made in
a worktree under `.claude/worktrees/`, never in the primary checkout, so
`.githooks/pre-commit` - which refuses a commit there while another session
is live - cannot strand a pull with a staged patch and nothing to show for
it. `pull` is idempotent: run again before that branch is merged, it finds
the branch already holding the mirror's edit and says so instead of trying
to recreate it; and if the edit is already in main with no branch at all -
merged by hand, as happened on 8 October 2026 - it finds that too (reversing
the mirror's diff applies cleanly against main) and reports nothing to pull.
`push` reads the same way: main already absorbing an edit the mirror's own
history does not yet show as ours is not a reason to refuse, and the commit
it makes lands on the mirror's tip to mark it absorbed even where the tree
itself does not change. A change under `figures/` on the Overleaf side is
refused outright: figures are built here, never hand-edited on either side.
`code/merge.sh` runs `pull` as its first step, so an Overleaf edit is never
overwritten by a thread's merge, and `push` as its last, so every merge
reaches Overleaf without anyone running a separate command.
`code/publish.py`'s own docstring has the reasoning for building this out of
plain git plumbing rather than `git subtree`, which handles one prefix and
not two.

`push` first reads the paper's `.tex` files at `HEAD` (the wrapper and
everything it `\input`s; the timelines live under `docs/`, outside the
mirror, so Overleaf never compiles them) and refuses if any path they load - a
font folder, a `\graphicspath` folder, a figure named outright, a bibliography, an
included file - is outside what the mirror carries. The first mirror lacked
the Lato files and Overleaf could not compile; nothing said so until
someone read a screenshot. A figure passed through a macro argument is
covered by the `\graphicspath` folders themselves.

Overleaf keeps its own server-side clone of each GitHub repository it is linked
to, keyed to the repository's identity and not its name. On 7 October 2026 that
clone was stuck at the 22 September state after the repository was renamed:
every pull showed the stale tree, and a fresh import pushed the stale tree back
into the mirror's `main` as "Merge overleaf-2026-10-07-1023 into main". Nothing
pushed to GitHub clears it. The one fix to try is a new repository, and so a new
identity, for the mirror, published to from `code/publish.py`, with a new
Overleaf project imported from it and the old project trashed.

## Why one repository, with `paper/` inside it

**One repository, with `paper/` inside it**, so the paper and the figures
stay beside the data and the code that produced them. Pushing figures across
a repository boundary would undercut the case that this setup is simpler than
emailing files. Overleaf sees only the mirror (above), so its limits - a
recommended 100MB in all, a hard 7MB of editable text - apply to what the
mirror holds, which is well inside both. Nothing in this repository
measures them.

Two choices were made when Overleaf still synced the whole repository, and
stand for their own reasons. The census scans the build never reads are
fetched on demand rather than committed, and so is the OCR of the census
volumes (`data/transcribed/by_ocr/`, regenerated on a Mac by
`code/transcribe/census.py`): both are bulk nothing reads. The raw tables and
outlines the build reads and nobody edits - everything under
`sources/government/federal/us_census_bureau/`, `sources/government/local/arlington_county/` and
`sources/government/state/va_dept_of_elections/` that is a CSV or GeoJSON - are
stored as `.csv.gz` and `.geojson.gz`, a fraction of the plain size. pandas reads a
`.csv.gz` as it reads a `.csv`, so only the paths and the checksums in
`data/contents.csv` changed; `data/built/` and `data/clean/` are
byte-identical to what they were. `write_text()` in `code/fetch/paths.py` writes the
gzipped form with no name or time in the header, so a refetch gives the same
bytes and the checksum holds. The census tables in `data/built/census.csv`
keep their names without the `.gz`, since clean steps look a table up by that
name. The IPUMS codebooks, the 1980 record layout and the README stay plain
text: nothing reads them, and a reader can open them.

## Why `sources/` is one folder, filed by group and publisher

**`sources/` holds every file as it was published, and `data/` holds the three
layers this repository makes.** The repository used to split published
material by who reads it: a raw folder inside data for what the build reads
and a documents folder inside sources for what the prose cites, and the line
sat where Overleaf's size cap had put it. That is not a difference in the
files. The Richmond Charter Review Commission's report sat in the raw folder because one
appendix table feeds a figure; it is a report. The split now is published
versus produced (Sally, 8 October 2026): everything published is under
`sources/`, and `data/` is `transcribed/`, `built/` and `clean/`.

**The groups.** Under `sources/`, a file is filed in `press/` (papers and
magazines, one folder per title, the Arlington Historical Magazine and Metro
Weekly among them), `legal/` (`cases/`, `constitutions/` and `statutes/`, the
last split into `state/` and `federal/`; the three the bibliography's Legal
Authorities part uses), `government/` (`federal/`, `state/` and `local/`, a
folder per body), `academic/` (a body tied to a university: IPUMS, the Data
and Democracy Lab, the law reviews), `genealogy/` (Ancestry, FamilySearch,
Find a Grave, WikiTree and Dignity Memorial) and `other/`, a folder per
publisher with no further grouping. `archive.SHELVES` lists the publishers in
each; a publisher it does not list goes to `press/` if its entry is a
paper's page and to `other/` if not. The grouping is a first scheme and is
expected to be revisited; only the rule below it, a folder named for who
published the file, is settled.

Four calls inside it. The pages we set out ourselves from an indexer's record,
which no one published as a file, are filed under the indexer, `genealogy/ancestry/`,
not under the body that made the original record. Arlington Connection and
Connection Newspapers are one folder, `connection_newspapers/`. MGGG Redistricting
Lab and the Data and Democracy Lab are one body renamed, filed as
`data_and_democracy_lab/`. And the Sun's mastheads stay separate folders
(`arlington_sun`, `arlington_daily_sun`, `northern_virginia_sun`,
`sun_gazette`, `arlington_daily`), because a citation names the masthead a page
was printed under. Four entries name no publisher a rule can read, and
`archive.PUBLISHER_OF` files them: Hjerpe's unpublished research under
`other/grace_hjerpe/`, Noetzel's 1907 map under
`government/local/alexandria_county/`, Gilbertson's book under
`other/national_short_ballot_organization/`.

**What it costs and what it commits.** `sources/` holds the cited copies and the
census sheet images, in plain git with no LFS, and the clone is large
(accepted by Sally, 7 October 2026). The build still reads only the folders
`code/build/paths.py` names, and `run.sh` keys the build cache on exactly those
folders, which `code/tests.py` holds together. A copy is committed beside its
citation for the same reason `data/clean/` is committed despite the usual rule
against committing generated data (above): a reviewer opens it from the same
clone that holds `paper/bib/sources.bib`.

**`sources/` holds nothing a resident wrote to the Board.** The County's
correspondence - 195 messages residents and others sent about the form of
government - stays in Drive, on purpose: a permanent indexed archive of
people's names, addresses and signature blocks is a different object from
the County's own file, whatever each letter's status under FOIA
(`docs/comments.md`). `data/transcribed/by_claude/comments.csv`, read from
that folder by `code/transcribe/comments.py`, is the repository's record of
it - a row per message with a count, never a name or a body - and is
committed like any other transcription.

**The repository is private because `sources/` and `data/` hold more than
this project's own words.** `sources/` files copies of licensed and
copyrighted material - HeinOnline session laws, newspaper scans, Ancestry
images, journal articles - for the authors' use, and `data/` holds IPUMS
extracts whose terms forbid redistribution; a public repository would
redistribute both.

Two large files cleared the fetch-on-demand bar the census scans use - a URL,
and no figure reads the file - but stayed committed rather than being made
`in_git = no`: the 1902 Virginia Constitution scan (50MB, from a Library of
Virginia delivery servlet whose URL is not a stable direct download) and the
1980 Census of Housing volume (29MB, from a plain Internet Archive link).
Building a second on-demand fetcher for two files, when the whole archive's
committed size was already weighed and accepted, is the kind of mechanism
this project's own rule against premature infrastructure warns against,
so both are plain committed files like the other 544.

**`run.sh` warns at 900MB of tracked files**, GitHub's comfort line for a
fresh clone being about 1GB; the fix it names is the one above, marking a
file `in_git = no` in `data/contents.csv` and fetching it on demand the way
the census scans already are. One warning, no hard stop.

`code/publish.py`'s mirror push only ever exports `paper/`, `figures/pdf/` and `style/fonts/`
from `HEAD` (`ALLOWED` in that file, checked again by `verify_tree()` right
before the mirror commits), so `sources/` was never at risk of reaching the
Overleaf mirror and needed no change to keep it out.

Every bib entry's annotation names its copy as "Filed in sources as" followed
by the path inside that folder, and `code/sources/archive.py` refuses a name
that is not there. `data/contents.csv` has a row for every file, with a checksum,
and `code/tests.py` refuses a file with no row or a checksum that has moved.

## Why the paper is one file per section under a folder per part

The paper is one file per section, under one folder per part:
`paper/1_history/`, `paper/2_community_input/` and `paper/3_future_work/`,
plus `paper/4_appendix.tex` for the Data Appendix, which holds no section
folder of its own since it is a single file, and `paper/0_summary.tex` for
the Executive Summary.
`paper/arlington-bsap.tex` is the wrapper: the preamble, the front matter, a
list of `\input` lines in reading order, the bibliography call and
`\end{document}`, and holds no prose of its own. A table under `paper/tables/`
follows the figure convention: `code/analysis/members_roster.py` writes the
whole file - title line, environment, rows and notes - and a section `\input`s
it by name, so a table with numbers in it is always built, never typed.

Two surfaces edit this paper, Overleaf and the repository's own Claude
threads, and they edit it concurrently. Edits to one file collide; edits to
different files combine. A single 1,400-line file put every edit in one
file's way of every other. A file splits when two people are in it at once,
not before: the split follows where the collisions actually happen, not a
guess at where they might.

Each section file's first line is `% revised: none` or `% revised: SH 7 October 2026` (a person's initials and the date, several separated by `; `), set only when a person has rewritten the section and not when they have read it; the contents page stamps it beside the section, a section whose subsections sit in files of their own reads draft while any of them does, and `code/revisions.py` prints the coverage.

## Why one session works on main and two take worktrees

Two sessions sharing one checkout once produced committed figures built
against uncommitted edits, so `figures/` no longer matched `data/clean/`
beside it. Since then a session that is not alone in a checkout takes a
worktree on a branch, and the hook in `.claude/settings.json` says at the
start of a session which case applies. It advises and never blocks, since
collaborators may be new to Git.

**The hook once judged this by counting worktrees, which misses simultaneous
starts.** `git worktree list` only grows once some session has already taken
a worktree; it says nothing about how many sessions are live in the primary
checkout before any of them has. Four sessions once started at once with
none, so all four read "0 other worktrees" and all four worked directly in
the primary checkout, which is the exact case the hook exists to prevent. The
hook now writes its own liveness marker instead: a PID and a timestamp in
`.claude/tmp/session.lock` (machine-local, gitignored), checked with `kill
-0` against whatever PID it finds there, ignoring one it wrote itself or one
past its shift. Two sessions starting in the same second each see the
other's PID as soon as either has written it, which a static count of past
worktrees cannot.

**Advice was not enough, so the shared checkout now refuses.** The hook above
speaks once, at the start of a session, and a commit comes hours later. Two
sessions worked in the primary checkout at the same time and a broad `git add`
in one of them swept the other's unstaged edits - a paragraph in
`docs/members.md` and a deleted row in `docs/questions.csv` - into a commit
whose message described neither. Nothing was lost; the cost is a commit whose
diff and message disagree, which the next reader cannot reconcile.

Staging explicit paths avoids that, but only for as long as everyone remembers
to, which is a mechanism where an invariant is available. `.githooks/pre-commit`
refuses a commit in the primary checkout while more than one session is live,
and names `git worktree add` in the refusal; `git commit --no-verify` is the
way past it for anyone who means it. A worktree has its own working tree, so
its commits can only hold its own edits, and the hook stays silent there.

This also changed how liveness is recorded. The single
`.claude/tmp/session.lock` held one pid, which each new session overwrote, so
it could answer "was anyone here when I started" and never "how many are here
now" - and a commit needs the second question. A directory of one file per
session replaced it, each named for the session's pid and pruned when the
process had gone. Both the SessionStart hook and the commit hook read it
through `.claude/sessions.sh`, so they cannot drift apart.

**A guard that reports nothing looks exactly like a quiet checkout.** That
pid directory never held anything. A session registered itself by writing a
file named `$PPID`, but in a hook `$PPID` is the shell that invoked the
script, which exits at once, so the next read found a dead process and
pruned the file. The directory was therefore always empty, every
SessionStart said "this is the only live session", and `.githooks/pre-commit`
never refused a commit in its life. It was found on 1 October 2026 with three
sessions live in the primary checkout, two of them committing.

Liveness is now read rather than registered: Claude Code writes a transcript
per session under `~/.claude/projects/<cwd with slashes turned to dashes>/`,
and a session is live if its transcript has been written to within the last
four hours. Nothing has to remember to announce itself, and the signal is
produced by the thing whose presence is in question. `code/tests.py` builds a
checkout with two live transcripts and one from yesterday and asserts the
count, because the failure mode here is silence; it also asserts that
transcripts which cannot be found stop the counter with an error instead of
an empty answer, which is the distinction the old design lost.

The hook is committed under `.githooks/` rather than left in `.git/hooks/`,
where it would be invisible to review and absent from a fresh clone. `run.sh`
points `core.hooksPath` at it and restores the executable bit, so no
collaborator has to install anything, and a clone that loses the bit does not
disarm it.

Collaborators each work in their own clone, so they cannot share a checkout;
they meet only at push, and a rejected push means pull, run the build again,
push. The build itself is reproducible: the same sources in a fresh virtualenv
give byte-identical figures, so two people who pull the same commit hold the
same `figures/`.

## Why merging a thread's branch is a script

A thread works in a worktree on a branch and ends with a push; its branch
comes back to main through `bash code/merge.sh <branch>`. The steps were done
by hand six times on 5 October 2026 - a scratch worktree, the merge, `bash
run.sh`, `code/paper.py`, the fast-forward, the push, the worktree and branch
removed - and three slips repeated: a commit chained after a failing build,
a brace dropped between two appended bibliography entries, and a figure
rebuilt in the worktree and lost when the worktree went.

The script does the same steps in the same order and refuses at each place a
hand slipped. It merges in a worktree taken from `origin/main` after a fetch,
so the merge is against what is pushed; a conflict in a row of the tracker or
outside the union-merged files (`.gitattributes`) stops it with the files named and main untouched,
because two sessions editing one line is a person's decision; the build and
both compiles run on the merged tree and a failure stops it before anything
reaches main; what the build rewrote is committed in the worktree before the
fast-forward, so a rebuilt figure travels with the merge; then main
fast-forwards, pushes, the compiled PDFs are copied to the primary checkout,
and the scratch worktree goes in the script's EXIT trap, on success as on
failure. One line prints per step, and the primary checkout must be on main and
clean, or it declines to start; run from a worktree it names the primary
checkout and the command to run there. The remote is always `origin`: the
override had no setter.

**What the script removes of the thread's own.** Two threads lost their
worktrees on 6 October 2026, probably to the leftover cleanup after a merge. The
thread's worktree and local branch now go only if three things hold: its branch
is merged into main, its tree is clean, and no live session holds it, which
`git worktree lock` says. Otherwise the script prints why the worktree stays.
`code/tests.py` merges with each of a clean, a dirty and a locked worktree.

**The tracker merges by row, not by line.** `docs/questions.csv` used to merge
by union, which keeps both sides of every differing hunk, and so resurrected
nine rows closed on main whenever a branch touched a line near them. The unit
of the file is the row, so `code/merge_questions.py` is a merge driver keyed on
the row id: each row takes the one side that changed it, a row both sides changed
differently is a conflict with both versions written between markers, and an
edit against a deletion is such a conflict too. The result is main's rows in
main's order, then the rows the branch added. Git keeps a driver in
`.git/config`, so `run.sh` registers it as it registers the hook path, and
`code/merge.sh` refuses to run without it. The union merge stays for the
punch list and the negatives file, which are append-only.

One conflict is settled by the script: a file under `figures/` or `data/clean/`
that one side deleted and the other rebuilt (modify/delete) takes the branch's
side, because the build recreates whatever the code still produces. The same
conflict anywhere else stops it, naming the file and the two commands that
resolve it each way.

`code/tests.py` builds a throwaway remote and clone and runs the script three
ways, with the build and compile commands substituted: a failing build leaves
main where it was, a passing build lands with the file it rewrote, and a real
conflict stops before building. Those are the three slips, each reintroduced.

The build and the compiles run on every merge, whatever the branch touched,
and are fast when it touched little because of the cache below, not because
the script decides what to skip.

## Why the build is cached, and where

The build and clean stages each run their steps in one Python process
(`code/stage.py`, which runs the figures too), so the interpreter
and pandas start once and not once per step. A cold `bash run.sh` went from
103 s to 70 s. The one piece of module-level state that would carry one step's
reads into the next, `code/build/paths.py`'s list of the tables a step read for
`write()`'s check, is cleared before each step.

A merge builds in a fresh worktree, and so does every thread. `run.sh` used to
judge a stage unchanged by its inputs' modification times, kept in a stamp in
`data/built/`; a fresh worktree has no stamp and gives every file the time of
the checkout, so every merge rebuilt and recompiled everything - about ninety
seconds on 6 October 2026, for a branch that changed one line of a write-up.

Each stage now has a key: a hash of the bytes of its inputs, the Python and
its installed packages, and `run.sh` itself. Before a stage runs,
`code/cache.py` looks for that key; if a run anywhere in the clone already
produced outputs from those exact inputs, they are copied back and the stage
prints what it printed then. Otherwise the stage runs and its outputs are
saved under the key. This is the model of ccache and of DVC's run cache,
small enough here not to need either.

| stage | inputs | outputs |
|---|---|---|
| build | the folders `code/build/paths.py` names under `sources/`, `data/transcribed/`, `code/build/`, `code/citekeys.py` | `data/built/` |
| clean | the build's key, `code/clean/`, `code/citekeys.py` | `data/clean/` |
| figures, on a full run | `data/clean/`, `code/analysis/`, `code/stage.py`, `style/` | `figures/`, the three `.tex` files the analysis stage writes |
| each compile | the files latexmk's record says the last compile read, `paper/*.bib`, `style/fonts/`, `code/paper.py`, the TeX version | the PDF |

The cache lives in `.git/build-cache/`, because every worktree of a clone shares
one `.git`: a merge worktree finds what the thread's worktree built, and nothing
in it can be committed. Eight entries are kept per stage. Deleting the directory
costs one full rebuild and nothing else.

The inputs are what git counts as the tree - tracked files and new ones not
ignored - read from disk, so an uncommitted edit counts and a fetched scan the
build never reads does not. A compile's inputs come from the `.fls` record
latexmk writes of every file lualatex opened, so no list is kept by hand. That
record from the last compile is enough: a document can only start reading a new
file through an edit to one it already reads, which changes the key. Two inputs
are not in the record and are added to the key directly: the bibliography,
which biber reads, and the typefaces, which LuaTeX loads through its own font
cache.

A filtered run (`bash run.sh <figure>`) always draws the figures it names; it
is for editing one. The tests always run on a full run: every merge changes
the tree, so a cached verdict would never apply.

`code/tests.py` reintroduces the mistakes that would make a cached output
silently wrong: a key that follows modification times, an uncommitted input
left out of the key, a restored table carrying the old time that
`code/clean/paths.py` refuses, a worktree keeping a cache of its own, the
compile record read from the wrong directory, and a bibliography edit that
leaves a compile's key unchanged.

## Why the paper compiles with lualatex, and the two ways it fails

`paper/arlington-bsap.tex` sets its body text in Lato, the typeface
`style/urban.mplstyle` gives the figures, so the report and the charts inside
it read as one document. Choosing a typeface by name needs `fontspec`, and
`fontspec` runs only under lualatex or xelatex, never under pdflatex. Both
authors and Overleaf therefore have to use the same engine, and the file says
which in its first line:

```
% !TeX program = lualatex
```

That is a magic comment. Overleaf and latexmk both read it and switch engines
on their own, which is why it lives in the file instead of in an Overleaf
project setting only one author can see.

The four Lato faces are committed under `style/fonts/` rather than installed,
so the fonts travel with the repository, and through the mirror to Overleaf, and to the other author's
machine. All four are declared in the preamble: an undeclared face is
substituted silently, which is the second failure below.

**Compiling with pdflatex stops with a fatal fontspec error**, naming the
engine it wants:

```
Fatal Package fontspec Error: The fontspec package requires either
XeTeX or LuaTeX.
```

This failure is loud and costs nothing. Compile with `latexmk -pdflua
arlington-bsap.tex` from `paper/`, or let an editor read the magic comment.

**A stale `paper/build/arlington-bsap.fdb_latexmk` silently drops every citation.**
That file is latexmk's record of which tools it ran last time. The paper uses
biblatex with `backend=biber`; if the record holds bibtex from an earlier
build, latexmk keeps calling bibtex, which finds no citations in a biblatex
document and reports errors most editors bury. The PDF still builds, and every
footnote citation and every `\ref` to a figure comes out undefined. It is the
dangerous failure, because a report that is missing its sources looks finished
at a glance.

`code/paper.py` handles both. It compiles, then reads the log, and treats an
undefined citation, an undefined cross-reference or a substituted font as a
failed build however latexmk exited — deleting the PDF rather than leaving one
that reads as finished. A stale record is the usual cause and clearing it is
free, so a first failure is retried from clean before it is reported. The
checking is a pure function over the log's text, `problems()`, which is why
`code/tests.py` can reintroduce all three mistakes without a LaTeX
installation.

On Overleaf, where that script does not run, the same staleness is cleared by
*Recompile from scratch*, under the Recompile dropdown. The symptoms to look
for are the same: `Font shape ... undefined, defaults substituted` means a face
is missing from `style/fonts/` or from the `\setmainfont` declaration, and
undefined citations mean biber did not run.

## Why the bibliography is checked entry by entry

`test_every_cited_entry_is_complete` reads the keys the paper's `.tex` files
cite and holds each entry to the style sheet below, through `incomplete()` in
`code/tests.py`. It refuses an entry that lacks what its kind prints (a newspaper
piece without a journaltitle, location, date, title or page; an online piece
without an organization or author, a date or a url; a report without an
institution or author and a date; a thesis without a school; a case without a
reporter; an act without its chapter and series; a book without a publisher and
year) and one that carries what the sheet forbids (a masthead that opens with
*The*, a title not in headline style, an unsigned piece whose `sortname` is not
braced, a signed one that has a `sortname`, an author equal to the journaltitle or
organization, a report whose institution is inside its author, an article read online with a url and no `entrysubtype = {magazine}`, a thesis url that
is a repository's home page, primary law typed as anything but `@jurisdiction` or
`@legislation` (a case with no `sortname`, a law with no `sorttitle`), a census record that is not `skipbib`, and a `note` over 80
characters). A field the copy does not give is declared in the annotation ("The
copy gives no page", "The page gives no date").

## The bibliography's style sheet, 4 October 2026

The Works Cited and the footnotes follow *The Chicago Manual of Style*, notes and
bibliography, as biblatex-chicago prints it. This sheet says, for each kind of
source, which fields an entry carries, how it reads in a footnote and in the Works
Cited, and where it sorts. `test_every_cited_entry_is_complete` enforces it for the
entries the paper cites. A rule says "Chicago" when the manual and the package
agree; a departure is marked **departs** and says why.

**For every entry.** A footnote is the citation and the page, nothing else: no URL,
no access date, no commentary (`note` carries a page, a volume or a reporter
citation, at most 80 characters; the rest goes in `annotation`, which biblatex does
not print). The Works Cited keeps the URL and drops the access date. Titles are in
headline-style capitalization whatever the source printed, with its spelling kept
(Chicago 8.159); a range in a title takes an en dash. A corporate author is braced,
`{{Arlington County Board}}`, and joint authors are joined with `and`. An entry that
lacks what its kind needs says so in `annotation` ("The page gives no date", "The
copy gives no page"). A citekey never changes.

**Newspaper piece, signed** (`@article`). `author` is the byline; `title` the
headline; `journaltitle` the masthead without its leading *The* (Chicago:
*Sun*, *Daily Sun*, *Evening Star*), set once, the same in every entry of that
paper; `location` the place of publication where the name does not give it
(Arlington, Va.); `date` the full date; `pages` the page as printed (A-26). Footnote
and Works Cited read `Sawicki, “Casto Enters Board Race,” *Northern Virginia Sun*
(Arlington, Va.), July 4, 1963, 1.` Sorts under the author's surname.

**Newspaper piece, unsigned** (`@article`). The same, with no `author`: the paper is
not an author, so its name is not repeated there, and `sortname` is the masthead,
braced as an organization (`{{Alexandria Gazette}}`; unbraced, biber reads it as a
person and files "Daily Sun" under S). Sorts under the masthead, then by title.
**Departs:** Chicago would open the entry with the paper's name; the drafting rules
open with the headline and file under the paper, which reads the same to a reader
looking the paper up.

**Online-only piece** (`@online`). `author` if signed; `title`; `organization` the
outlet as it names itself (ARLnow, InsideNoVa); `date`; `url`. Set in roman as
Chicago sets a website. A piece a print paper wrote and a site reproduces is an
`@article` of that paper, never "via" the host: *Sun Gazette* (Arlington, Va.),
with the URL saying where it was read, the annotation saying the copy gives no
page, and `entrysubtype = {magazine}` so the footnote, which drops the URL, does not
end in a comma. Unsigned: `sortname` is the outlet, braced. A page that carries no date has
no `date` field and the annotation says "The page gives no date".

**Report or document by a body** (`@report`). `author` the body or the person;
`title`; `institution` the publisher, only when it differs from the author (the same
name twice prints twice); `date`; `url` when the public can reach it. Sorts under the
author.

**Journal article** (`@article`, with a volume). `author`, `title`, `journaltitle`,
`volume`, `number`, `date`, `pages`, `url`. Where the copy prints no volume or
issue (the *Arlington Historical Magazine* pages we hold), the entry gives the month
and year and the annotation says the copy prints neither.

**Book** (`@book`). `author` or `editor`, `title`, `location`, `publisher`, `date`;
`url` for a scan. **Thesis** (`@phdthesis`): `author`, `title`, `subtype`,
`institution`, `date`, and a `url` that reaches the document itself (the repository's
handle), not the repository's home page.

**Primary law is cited in notes and listed once, in Legal Authorities (a plainer name for what a legal brief calls
its Legal Authorities), not the
Works Cited.** Chicago 14.275 and the Bluebook agree that law is not a bibliography
item. `\printworkscited` leaves the two legal types out, and `\printauthorities`
(`paper/bib/bibstyle.tex`) lists them after it under Cases, Constitutions and Statutes,
each with the pages that cite it (`backref=true`). `@misc` and `@online` would have
printed in the Works Cited, which is how some Commonwealth entries listed and some
did not. Every case, act, session-law volume, constitution and code section is
therefore a `@jurisdiction` or a `@legislation`; scholarship or a memo about law is an
ordinary article, report or book and prints in the Works Cited. A legal entry carries
no `author`: the sovereign is named by the reporter or the volume (`organization`
holds it for filing). Cases sort by a braced `sortname` equal to the caption, and
statutes and constitutions by a `sorttitle` equal to their date, which is what orders
the table. `code/sources/cite.py` writes all of this.

- *Case* (`@jurisdiction`): `title` the caption with "v."; `journaltitle` the
  reporter abbreviation, `volume`, `pages` the first page; `origlocation` the parallel
  reporter; `location` the court only when the reporter does not say (a circuit
  court); `date` the decision, printed as its year. `Bennett v. Garrett, 132 Va. 397,
  112 S.E. 772 (1922).` An unreported case gives its number and court
  (`number`, `location`). **Departs:** none; the court name that the old `note`
  carried is dropped because "Va." says it.
- *Act*: `Act of Mar. 20, 1930, ch. 167, 1930 Va. Acts 450.` `title` "Act of" and the
  date of approval, `titleaddon` the chapter, `shortjournal` the session-law series,
  `volume` its year, `pages` the first page, `shorttitle` the same as the title (a
  later note would otherwise print the chapter alone), `keywords = {datedintitle}`
  because the date is already in the title, which `paper/bib/bibstyle.tex` reads. The
  act's own long title is in `annotation`. A volume
  cited at several chapters (the Acts of 1869–70) is one entry, titled "Acts of the
  General Assembly, Session of 1869–70", and the chapters go in the pin.
- *Constitution*: `Va. Const. of 1869, art. VII, sec. 2.` `title` "Va. Const. of 1869",
  `entrysubtype = {constitution}`, the article and section in the pin.
- *Code*: `Va. Code Ann. § 15.2-1422 (2020).` `title` carries the section
  (`Va.\ Code Ann.\ \S~15.2-1422`), `date` the year of the text read; the section's
  heading goes in `annotation`. An old code is cited like a volume of acts, its
  title carrying its year (`Code of Virginia of 1860, ch. 53, secs. 1 and 3`).

**Census record** (`@misc`, built by `code/sources/ancestry.py`). A single
enumeration line is cited in notes only (`options = {skipbib}`); the Works Cited
does not list individuals from a schedule. The footnote gives the person, the
census and place, the database and the record number.

**Dataset or database page** (`@dataset`, or `@online` for a page): `author` the
publisher, `title`, `version` if any, `date` if the page gives one, `url`.

## What `code/tests.py` guards

A guard gets a test when removing it would let the build ship a plausible
wrong number. A guard whose absence makes the build stop anyway (a
`KeyError` on the next line, a `min()` of an empty list) is not tested; it
would improve a message and nothing else.

Each test reintroduces the mistake and asserts the build refuses it. The
file repeats one pattern on purpose: a unit test against a planted input
that should fail, its mirror that should pass, and an integration test
against the real committed data, so one guard is exercised at two
distances from the data.

**A mangle must change something.** `breaks()` compares every value its
mangled function hands the build with what the original hands it, and a run
in which none differed raises `NothingMangled`. A test whose anchor row is
missing (stale `data/built/`, a filter that matches nothing) therefore
fails with that message and cannot read as a guard that did not fire.

`code/tests.py <word> ...` runs only the tests whose names contain a word.
