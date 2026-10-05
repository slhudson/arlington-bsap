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
from the layers above, and would add 1.6MB to the text Overleaf syncs.
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

The one exception is twenty-four census scans the build never reads, about
250MB that would push Overleaf past its ceiling. They are marked `in_git = no` in
`data/contents.csv` with their URL and checksum; `code/fetch/census_volumes.py`
fetches them and refuses a byte that differs, and `run.sh` says at the end of
every build if they are missing. A raw file the build reads is always
committed.

## Why one repository, with `paper/` inside it

**One repository, with `paper/` inside it.** Overleaf syncs a whole
repository and cannot be scoped to `paper/` and `figures/`, so it carries the
data too. Its limits are on the files it syncs, not on git history: a
recommended 100MB in all, and a hard 7MB on editable (text) files, past
which GitHub sync stops working. One repository was chosen because pushing
figures across a repository boundary would undercut the case that this setup
is simpler than emailing files. `run.sh` warns at 80MB and at 6MB of text, so
revisiting does not depend on anyone remembering; a gzipped file is counted
against the whole, not against the text, since it is not editable. The scans the build never
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
collaborator has to install anything, and Overleaf stripping that bit does not
disarm it.

Collaborators each work in their own clone, so they cannot share a checkout;
they meet only at push, and a rejected push means pull, run the build again,
push. The build itself is reproducible: the same sources in a fresh virtualenv
give byte-identical figures, so two people who pull the same commit hold the
same `figures/`.

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
so the fonts travel with the repository to Overleaf and to the other author's
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

**A stale `paper/arlington-bsap.fdb_latexmk` silently drops every citation.**
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
`@legislation`, a census record that is not `skipbib`, and a `note` over 80
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

**Primary law is cited in notes and never listed.** Chicago 14.275 and the Bluebook
agree, and biblatex-chicago skips it by default for `@jurisdiction` and
`@legislation`; `@misc` and `@online` do not skip it, which is how the Works Cited
came to list some Commonwealth entries and not others. Every case, act, session-law
volume, constitution and code section is therefore a `@jurisdiction` or a
`@legislation`, and scholarship or a memo about law is an ordinary article, report or
book and does print. A legal entry carries no `author`: the sovereign is named by the
reporter or the volume (`organization` holds it for filing).

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
  because the date is already in the title, which `paper/bibstyle.tex` reads. The
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

## What `code/tests.py` guards, 1 October 2026

A read of every test, each checked against the guard it names and against
what else in the file exercises the same code.

**No test guards something its own code path no longer reaches.** Every
test passes against the current build, and the substring each one checks
for in a raised message is still live in the module it mangles.

**No two tests guard the same failure the same way.** The file repeats one
pattern on purpose, four times over - a unit test against a planted input
that should fail, its mirror that should pass, and an integration test
against the real committed data - for press-copy naming, obituary naming,
quotation support, and citekeys named in prose. Those are not duplicates;
they are the same guard exercised at two distances from the real data,
which is the file's stated design.

**Three pairs guard the same mechanism on different columns, and could be
folded into one parametrized test each:**

- `test_race_and_gender_must_account_for_the_same_seats` and
  `test_party_must_account_for_the_same_seats` both mangle
  `members_by_year.months_held` and check that a column's values are
  accounted for against the seat table - gender in one, party in the
  other.
- `test_an_age_group_left_out_of_every_band_is_refused` and
  `test_an_age_group_claimed_by_two_bands_is_refused` both mangle
  `residents.STF_AGE_GROUPS` and check the same partition invariant from
  its two sides - a group named by no band, a group named by two.
- `test_more_board_voters_than_registered_voters_is_rejected` and
  `test_more_board_voters_than_presidential_voters_is_rejected` both guard
  a reasonableness ceiling on `elections_turnout`'s board vote, against two
  different ceilings.

Each pair would read as one test looping over its two cases, with the
column or ceiling and the expected message as the loop variable. Left as
written, nothing is wrong - the three pairs together are six tests, not an
unbounded pattern - so this is a proposal, not a finding of accretion.

**A guard with no test, by file, where `grep` finds no test checking for
its message anywhere in `code/tests.py`:**

- `code/clean/members.py` - three of the five party-conflict checks in
  `party_of()` and `party_attributions()`: two sources disagreeing on a
  term's party before the county is consulted (:119), the county itself
  printing more than one label for a term (:140), and a name's own
  attribution conflicting with the county's label (:159). The fourth and
  fifth (an unrecorded label, the county conflicting with the state) are
  tested. `birth_year must be a four-digit year` (:378) is untested.
- `code/clean/members_roster.py` - the two checks that the Jefferson rows
  joined into Edward Duncan's term leave no gap and do not overrun it
  (:134, :138).
- `code/clean/members_roster_novack.py` - both checks in the
  appointment-to-departure dating pass: an ambiguous appointment left with
  no dated departure (:77), and an open term whose member never stood
  again (:186).
- `code/clean/members_roster_arlhist.py` - the parsing guards that a
  rename, a note, a seated-date or a vacated-date names exactly one
  roster row (:319, :334, :390, :460), and that the article's seat block
  for a name exists and sequences as the roster expects (:376, :417, :471,
  :473, :490, :495, :541). One of this module's checks is exercised,
  through `test_the_seat_table_reads_the_roster_for_1912_to_1931`; the
  rest are not.
- `code/clean/members_roster_results.py` - county and state sources
  disagreeing on a year in their overlap (:82), and the two checks on a
  special election's winner (:117, :126).
- `code/clean/members_residence.py` - a place string no precision rule
  reads (:46).
- `code/clean/elections.py` - a candidacy carrying more than one label, and
  a label this build has no category for (:72, :75); a selected election
  row with no four-digit year (:184).
- `code/clean/elections_results.py` - a year where neither nominee's line
  matches (:90).
- `code/clean/elections_turnout.py` - the roster naming more terms
  beginning after a cutoff than the turnout series expects (:74), and no
  district election found with a count in every district (:117).
- `code/clean/candidates.py` - a ranked-choice contest whose first choices
  do not add up (:86), a name standing in more terms than `members.csv`
  records or in more than one contest a year (:108, :116), and the
  Jefferson District win count against Hjerpe's (:174).
- `code/clean/localities.py` - an unrecorded mayor (:27), a membership
  count outside the Code's three-to-eleven range (:47), and other than
  exactly one Arlington row (:50).
- `code/clean/census.py` and `code/build/census.py` - each has its own
  "expected Arlington's one row" guard (:46 and :28); neither is tested.
- `code/build/localities.py` - a peer locality named in the crosswalk that
  the census source does not carry population or land area for (:72).

That is not every `assert` or `raise` in `code/`; it is every one whose
failure would be silent in the sense `CLAUDE.md` means - a build that
keeps running and ships a plausible wrong number - rather than a type
error or a KeyError that would stop the build output anyway. Whether each
one is worth a test is Sally's call per guard; a few read as reachable only
through a hand-edit of the source data these modules take as fixed, which
is the kind of guard the existing suite tends to leave untested elsewhere
in the file too.

### Which of those thirty get a test

Each guard above read once more, asking the question `CLAUDE.md` asks:
delete it, and does the build ship a wrong number, or does it stop anyway?
Eighteen get a test, and each is proved: with its guard removed, the test
fails. Seven do not, and one already has a test.

**Eighteen get a test, because removing the guard leaves a code path that
produces a value.** They fall into five shapes, and the shape is what a
test reintroduces:

- *A conflict resolved by taking the first value.* The two party checks
  in `code/clean/members.py` that no other test reaches and the label
  check on a candidate's line in `code/clean/elections.py` are each
  followed by a line that reads `printed[0]` or `labels[0]`, so without
  the guard one of two disagreeing sources silently wins. So does the 2021
  overlap check in `code/clean/members_roster_results.py`.
- *A value that falls through to a default.* A place no precision rule
  reads returns `None` from `code/clean/members_residence.py`; an
  unrecorded mayor in `code/clean/localities.py` drops a mayor who sits on
  the council.
- *Votes in the wrong band.* A year matching neither nominee in
  `code/clean/elections_results.py` leaves both at zero.
- *A count or a denominator that moves.* Both checks in
  `code/clean/elections_turnout.py`, three of the four in
  `code/clean/candidates.py` including the pinned Jefferson win count, and
  the Code's three-to-eleven range and the one-Arlington-row check in
  `code/clean/localities.py`.
- *The wrong county's row, or none.* `code/clean/census.py` and
  `code/build/census.py` each guard Arlington's one row, and without it
  `.iloc[0]` takes whichever row is first; `code/build/localities.py`
  guards a peer the census carries no population or land area for.

The eleven parsing guards in `code/clean/members_roster_arlhist.py` are
the same mechanism on five declared tables: a rename, a note, a seated
date or a vacated date must match exactly one roster row, and a mis-typed
entry silently does nothing instead. One test that mangles one table
reintroduces that mistake for all of them.

**Seven do not, because the build stops anyway.** Each of these improves
a message and nothing else, which is not what `CLAUDE.md` reserves a
test for. The two checks on Edward Duncan's joined term in
`code/clean/members_roster.py` are caught by `check_seats` a few lines
later, which sees the gap as a seat held by nobody or the overrun as a
seat held twice. `code/clean/members_roster_novack.py` and
`code/clean/members_roster_results.py` each take `min()` of a list the
guard has just found empty, so both raise either way. A birth year that
is not four digits is caught by the age-when-seated range. A label with
no category raises a `KeyError` in both steps that read it, and a
ranked-choice contest with no recorded outcome raises a `KeyError` on
the lookup that follows its check.

**One already has a test.** A name's own attribution conflicting with the
county's label, in `code/clean/members.py`, fails
`test_reporting_cannot_overrule_a_party_the_county_prints` with the guard
removed; its message is shared with the state check beside it, which is
why a search for the message does not find it.
