---
name: sources
description: Add, fetch, cite or file a source for the Arlington BSaP report. Use whenever a document, dataset, census record, article or web page is being brought into data/raw/, cited in paper/sources.bib, or filed in sources/documents.
---

# Sources

`CLAUDE.md` has the rules: `data/` holds what we take numbers out of, a
source consulted only to settle a question is cited in `paper/sources.bib`
and filed in `sources/documents`, every source column holds a citekey, and a
bib entry is built from the document in hand. This file is the tools that do
it.

## Fetching a source the build reads

A source a figure derives from is fetched by a script in `code/fetch/`,
saved into `data/raw/` under the name of who published it, given a row in
`data/contents.csv` with its checksum, and committed. `run.sh` never touches
the network, so the build reads only what is committed. `docs/web_access.md`
says what each site needs from this machine.

## Which browser reads a page

A site that puts a human check in front of its pages - loc.gov, Virginia
Chronicle, HathiTrust, Ancestry, ProQuest, the Post; `docs/web_access.md`
names each - is read in Sally's own Chrome through Claude in Chrome, from the
first request. The built-in browser pane is a fresh browser with no history:
the check refuses it and shows a button nobody can click from inside Claude,
so a session that starts there and switches to Chrome after the refusal has
spent the first half for nothing. The pane is for sites that do not check.
A step that needs Sally's click - the check itself, a sign-in - is set up for
her: the page open in her Chrome and the ask at the top of the message; it is
never logged as a row with the session reporting "done". Saving a page's PDF
to `~/Downloads` is not one of those: once the check is passed, Claude clicks
the page's Download PDF button itself (Sally, 6 October 2026: standing
permission for newspaper page PDFs from loc.gov and Virginia Chronicle, a
page or two at a time), reads the file, and moves it on to `sources/documents`. Asking her
to click it is the friction this line removes.

## Before saying no source exists

Grep `paper/sources.bib`, `docs/` and `data/transcribed/` for the subject
first. A thread concluded on 6 October 2026 that no map drew the district
lines while `hjerpe2021` sat in the bibliography; a held source outranks a
search, and the search is not finished until the held ones are read.

## A hard read is a tracker row

A number read off a scan where two digits print alike (the 1890 volume's
1,620 or 1,820) is keyed with the reading chosen and why, and the row goes
in `docs/questions.csv` in the same commit, naming the other reading and what
it would move. A flag in `data/contents.csv` or a sentence in `docs/` is not
enough: nothing reads those for open questions, and Sally had to ask for the
row.

## Citing and filing a source the prose reads

`code/sources/cite.py` fetches such a source, files it and writes its bib entry in one
step; the note, what the document says, is still written by the reader, and
goes in the annotation: the paper prints a `note` field in every footnote, so
`note` holds only citation facts (`--cite-note`).
`code/sources/ancestry.py` does the filing for a census record, whose page is behind a
sign-in and cannot be fetched at all: it sets the record out on a plain page
from the row that already holds it, so the filed copy follows the row rather
than being made by hand.

## Reading an image

**Nothing leaves an image on one reading.** A census record is read against
its own enumeration sheet before any of its fields is used, and the row's
`checked` column says what the sheet gives. Ancestry's index is a finding
aid, the same standing as the OCR under `data/transcribed/by_ocr/`: it
locates the line, it does not read it. That is a second reading of every
record, not a sample, because the records are few and the cost of a wrong
one is silent. `code/build/members_claims.py` enforces the half a machine
can check: a row whose `checked` names neither the sheet nor the index stops
the build, and so does a `place` on a row the sheet was never read against,
since a street is the field the index gets wrong. `code/tests.py`
reintroduces both mistakes.

A field that stays uncertain is read a second time off the filed image,
enlarged with its column heading and set against the same enumerator's hand
elsewhere on the sheet (his D in *Daughter*, his 0 in another age). Where
the two readings still disagree, a source outside the sheet settles it, not
a third reading of the same smudge.

For a page read through OCR, a newspaper claim in `members_residence.csv`,
the quoted sentence is read off the page image before the row is written,
and any house number in it is read off the image, never off the OCR. Rows
entered before this rule are cleared a page at a time, whole pages, not a
sample of rows, since opening the page is the cost and the rows on it are
then free.

What each census column holds is in the docstring of
`code/clean/members_census.py`; a row's `basis` and `match` say what ties
the record to the member, and a name alone is no match.

## sources/documents

Committed in the repository, beside its citation: moved out of the
project's Drive on 7 October 2026 (`docs/repository.md`), so a cited copy
sits next to `paper/sources.bib` rather than off in Drive. The folder is
filed by kind, and its index is generated.
`code/sources/archive.py` files the documents folder into `legal`, `reports`, `books`, `bios`,
`campaign websites`, `press`, `obituaries` and `census`, the kind being a rule on the
bib entry; writes `index.md` at its top from `paper/sources.bib` and
`data/contents.csv`, so the index cannot drift from either; and builds the
zip the County receives, the repository at HEAD with the on-demand
scans and the folder. Without `--apply` it only reports. It refuses to act
while a name the bib says is filed is not in the folder, and deletes
nothing: a file no entry names goes to `unplaced/`.

Three kinds are split into subfolders by `archive.subfolder()`, because one flat
folder stopped answering a question: census by who made the copy and then the
census year, press by outlet so a paper's run is in one place, and legal by what
the document is — `opinions`, `statutes` or `constitutions`. A legal copy that
is none of those three stops the run, because that folder holds primary law
only: scholarship about law belongs in `books` and a legal memo in `reports`.

Four press folders are one paper under four mastheads. It debuted in December
1935 as the *Sun*; the separately published *Arlington Daily* (1939-51) merged
into it to form the *Daily Sun*; new owners renamed it the *Northern Virginia
Sun* in 1957; and it spent its last quarter-century as the weekly *Sun Gazette*,
which stopped in February 2023, its staff going to the *GazetteLeader* and then
to Local News Now, which publishes ARLnow. That is why one reporter's byline
appears under both Sun Gazette and ARLnow. The folders stay separate, one per
masthead, because a citation names the masthead a page was printed under and no
document on the shelf asserts the corporate chain; the chain is recorded here
instead. The *Arlington Daily* folder is a different paper, not an earlier name
for this one. (Lineage from ARLnow, 12 December 2024, "Arlington print
newspapers face thinning ranks after a vibrant history"; if the report comes to
rely on it, it needs an entry in `paper/sources.bib` of its own.)

A copy is named `<who> <year> - <title>.pdf`, and `archive.canonical()` decides
the `<who>`, renaming a copy whose name does not match when it files it. Three
rules, each from how its folder is read. A press copy leads with its outlet,
never its byline, because the question asked of that folder is what a paper
printed: `ARLnow 2026 - ...`, with a leading article dropped so papers do not
shelve under *The*. An obituary leads with the person it is for, from the
entry's `subject`, which is the roster's name for them and not always the
headline's, and carries its outlet after the title: `Grotos 2019 - Two-Term
Arlington Board Member Dorothy Grotos Dies at 88 (Sun Gazette).pdf`. Every
other kind leads with its author. A new obituary must set `subject` to a name
`data/clean/members.csv` also holds, or `code/tests.py` refuses the build.

`code/sources/clippings.py` cuts a copy printed from a web page back to where
its text stops, and `code/sources/scans.py` re-encodes the images of a copy
that was stored wastefully - a photograph kept losslessly, a page scanned far
above reading resolution - keeping every page and only where re-encoding at
150 dpi halves the file, so an archival scan of small print is left alone. Each
records what it did in the entry's annotation, which is also what stops it
running twice over the same copy.

**Another locality's own page about its governing body is cited and never
filed.** What the report takes from one is how many voting seats the body has;
that is keyed into `data/transcribed/`, with the url and the date read, and the
keyed row is what a reviewer checks. A screen capture of a council's
photographs attests nothing the row does not, and the peer set runs to seventy
of them - 45 reached the folder in a day, 257MB, before the rule existed.
`archive.roster_page()` is the rule, `code/sources/cite.py` refuses to file one,
and `code/tests.py` refuses a bib that names a copy of one or that does not say
where the count was keyed. The thirteen Virginia counties are the model: the
annotation ends "The count is keyed into
`data/transcribed/by_claude/county_boards.csv`; no copy is kept", naming
whichever table holds it.

## Citekeys

Three values are not citekeys and `code/citekeys.py` says what each admits
to: `assumed`, `derived`, `unsourced`. Anything else in a source column must
be an entry in `paper/sources.bib`, or the build stops. What is missing from
the copy we hold goes in the entry's `annotation`, which biblatex does not
print.

## Quoting a legal source

`code/sources/quotations.py` checks every entry filed under `legal/` against its own
copy: a quotation in the annotation that the filed document does not contain
stops the build. Quote the document as it prints the words. Where the
annotation quotes words for another reason - a recorded negative, a phrase
another entry supplies, a passage on a page the OCR did not reach - declare
it in `DECLARED` in that file with the reason. `code/tests.py` runs the check
on every full `bash run.sh`.
