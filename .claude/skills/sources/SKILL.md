---
name: sources
description: Add, fetch, cite or file a source for the Arlington BSaP report. Use whenever a document, dataset, census record, article or web page is being brought into data/raw/, cited in paper/sources.bib, or filed in the project's Drive folder.
---

# Sources

`CLAUDE.md` has the rules: `data/` holds what we take numbers out of, a
source consulted only to settle a question is cited in `paper/sources.bib`
and filed in Drive, every source column holds a citekey, and a bib entry is
built from the document in hand. This file is the tools that do it.

## Fetching a source the build reads

A source a figure derives from is fetched by a script in `code/fetch/`,
saved into `data/raw/` under the name of who published it, given a row in
`data/contents.csv` with its checksum, and committed. `run.sh` never touches
the network, so the build reads only what is committed. `docs/web_access.md`
says what each site needs from this machine.

## Citing and filing a source the prose reads

`code/sources/cite.py` fetches such a source, files it and writes its bib entry in one
step; the note, what the document says, is still written by the reader.
`code/sources/ancestry.py` does the filing for a census record, whose page is behind a
sign-in and cannot be fetched at all: it sets the record out on a plain page
from the row that already holds it, so the filed copy follows the row rather
than being made by hand.

## The Drive folder

The folder is filed by kind, and its index is generated.
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
