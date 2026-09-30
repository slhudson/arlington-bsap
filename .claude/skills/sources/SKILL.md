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

`code/cite.py` fetches such a source, files it and writes its bib entry in one
step; the note, what the document says, is still written by the reader.
`code/ancestry.py` does the filing for a census record, whose page is behind a
sign-in and cannot be fetched at all: it sets the record out on a plain page
from the row that already holds it, so the filed copy follows the row rather
than being made by hand.

## The Drive folder

The folder is filed by kind, and its index is generated.
`code/archive.py` files the documents folder into `legal`, `reports`, `books`, `bios`,
`campaign websites`, `press`, `obituaries` and `census`, the kind being a rule on the
bib entry; writes `index.md` at its top from `paper/sources.bib` and
`data/contents.csv`, so the index cannot drift from either; and builds the
zip the County receives, the repository at HEAD with the on-demand
scans and the folder. Without `--apply` it only reports. It refuses to act
while a name the bib says is filed is not in the folder, and deletes
nothing: a file no entry names goes to `unplaced/`.

## Citekeys

Three values are not citekeys and `code/citekeys.py` says what each admits
to: `assumed`, `derived`, `unsourced`. Anything else in a source column must
be an entry in `paper/sources.bib`, or the build stops. What is missing from
the copy we hold goes in the entry's `annotation`, which biblatex does not
print.

## Quoting a legal source

`code/quotations.py` checks every entry filed under `legal/` against its own
copy: a quotation in the annotation that the filed document does not contain
stops the build. Quote the document as it prints the words. Where the
annotation quotes words for another reason - a recorded negative, a phrase
another entry supplies, a passage on a page the OCR did not reach - declare
it in `DECLARED` in that file with the reason. `code/tests.py` runs the check
on every full `bash run.sh`.
