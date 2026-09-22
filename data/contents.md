# Contents of data/

Four layers, sorted by how the numbers were produced. Which folder something
belongs in depends on that, not on what it is about.

| Folder | How it was produced | Read by |
|---|---|---|
| `raw/` | published, as it exists in the world | `build/` |
| `transcribed/by_ocr/` | an OCR engine read the text layer | people |
| `transcribed/by_claude/` | a vision model read a rendered page | `build/` |
| `transcribed/by_human/` | a person checked it | `build/`, in preference |
| `transcribed/by_human/` | keyed in by a person | `build/` |
| `clean/` | computed by `build/` from `raw/` and `transcribed/by_human/` | `analysis/` |

A file in `raw/` is its own citation: the volume is the evidence. A file in
`transcribed/by_human/` is not — someone read something and typed a number, so it needs a
citation per cell. That difference is the whole of the sourcing problem, and
`docs/sources.md` tracks it.

`transcribed/by_ocr/` is absent from `build/files.py` and `analysis/files.py` by
design. OCR misreads digits, so it is a finding aid: it locates a table and a
page, and never supplies a number. `transcribed/by_claude/` is the other half of
that — the table transcribed once the OCR found the page, with the volume,
table and page in the filename so anyone can check it against the scan.

---

## raw/census/

Extracts from the published 1870, 1880 and 1890 decennial census volumes,
gathered by Alex Keena in September 2026 while correcting the 1870–1890 county
population figures. Received 2026-09-22. Nothing here should ever change; the
checksums are so that a change would be noticed.

Where exactly they came from is not recorded. The filenames match how the
Census Bureau chunks its scanned volumes, but that is an inference — see
`docs/questions.md`.

| File | Pages | Text layer | SHA-256 (first 16) |
|---|---|---|---|
| `1870a-01.pdf` | 6 | no | `207a404c63c65609` |
| `1870a-04.pdf` | 36 | no | `0dc7a2a508ffe416` |
| `1870a-09.pdf` | 46 | no | `63f3d4eaac112736` |
| `1880_v1-12.pdf` | 72 | yes, poor OCR | `acc0b1ab4dd6ee88` |
| `1880_v1-13.pdf` | 85 | yes, poor OCR | `6e859908a8bd2a5d` |
| `1890a_v1-11.pdf` | 86 | no | `47903c2e2ec9ed46` |
| `1890a_v1-12.pdf` | 24 | no | `782da690cdf3ca40` |
| `1890a_v1-13.pdf` | 93 | no | `fb1d9e704366cbf4` |
| `1890a_v1-14.pdf` | 73 | no | `42c36586ed15d9f0` |

Seven of the nine have no text layer at all.

## transcribed/by_ocr/

OCR of all 521 pages, one text file per volume, produced by
`build/ocr_census.py` using macOS Vision. Not part of `bash run.sh` — it takes
about twelve minutes and its input never changes.

Use it to find a table and a page. Do not read numbers from it: OCR of
19th-century tables misreads digits routinely, and the text layer already
embedded in the 1880 files renders 13,659 as `lB, 659`.

## transcribed/by_claude/ and by_human/

Transcribed source tables, one file per printed table, laid out as the table is
laid out rather than reshaped into whatever a script wanted. Transcribing the
whole table means it can be checked against the page as a whole — a missing row
or a misaligned column shows up, where a list of extracted values hides it.

`by_claude/` is a machine's reading of a page image: better than OCR, wrong in
different ways, and confirmed by nobody. `by_human/` holds tables a person has
checked, and `build/` prefers it for the same table, so confirming something
changes what gets built. It is empty, which is honest.

Files are named `<volume>_p<printed page>_table<n>_<state>_<subject>.csv`, so
the filename is the citation.

Each row carries the printed indentation as a `level` column: 0 is the table's
own total, 1 its parts, 2 a detail of the line above. Sums take level 1 only.
Freedman village is printed at level 2 inside Arlington district, so it cannot
be added as a fourth district — the error that produced 4,596 is
unrepresentable rather than merely warned against.

No arithmetic lives in these files. Before 1900 no published table gives the
territory the Board governed, and that subtraction happens in
`build/residents.py`.

Seven tables so far, covering Alexandria County and city for 1870, 1880 and
1890. Four values were read twice from different volumes and all four agreed.

## manual/

**The three workbooks are under glass.** They are exactly as Alex Keena
delivered them on 2026-09-22 and are never edited here. A discrepancy is
recorded, not corrected.

`census_verification.csv` is the exception: it is compiled in this repository
rather than received, and holds the running record of which workbook figures
have been traced to a source table. See `docs/sources.md`.

**`arlington county demographic data.xlsx`** — 16 census years, 1870–2020:
population totals, race and ethnicity counts, Board seats, and derived
residents-per-seat and cube-root columns. Two source URLs sit in rows below the
data, with no record of which years each covers. The 1870–1890 rows were
corrected in September 2026, after the original figures were found to include
the City of Alexandria, which the Board did not govern.

**`arlington board - descriptive representation (1870-2026).xlsx`** — 156 years
of Board seat counts by race/ethnicity and gender, 1871–2026. No sources
recorded. The header `aapi_m embers` contains a space, corrected in
`build/board_seats.py` rather than here.

**`arlington county board member database (1932-2026).xlsx`** — 497
person-years, 1932–2026, one row per member per year, race and gender coded on
every row. No source column yet; that is item 6 of the work order in
`docs/sources.md`.

| File | SHA-256 (first 16) |
|---|---|
| `arlington board - descriptive representation (1870-2026).xlsx` | `b5de85deed3414fc` |
| `arlington county board member database (1932-2026).xlsx` | `66b511fddac149df` |
| `arlington county demographic data.xlsx` | `fcf4d9bdb4779ae1` |

### The Board data has no raw layer

The census figures have published volumes sitting under them in `raw/`. The
Board figures have nothing. Both Board workbooks rest on news coverage, the
Arlington Historical Society and obituaries, none of which is in this
repository in any form — so for 1871–2026 the manual file *is* the only record,
and the coding cannot currently be traced or checked by anyone else.

That is why a `source` column matters more for the Board files than for the
census.

## clean/

Written by `build/`, read by `analysis/`. Never edited by hand; `bash run.sh`
overwrites it. Committed even though it is generated, so that a change to a
cleaning decision shows up as a reviewable diff — you can see which numbers
moved and by how much.

`residents.csv` · `board_seats.csv` · `board_members.csv`

`residents.csv` carries a `source` column naming the document behind each row —
`census volumes` for 1870-1890, `census county series` for 1900-1990,
`workbook` for what has not been traced to a published source yet. The
workbooks are a way station, not a permanent input, and that column is where
the remaining distance shows.

## raw/census/ — Census Bureau data files, 2000-2020

For 2000, 2010 and 2020 the Bureau publishes machine-readable data, so there is
no page to read and no transcription step — and therefore no reading error to
make. `build/fetch_census.py` saves each table whole: one row per Virginia
county, one column per variable, exactly the shape it is published in.
Arlington is a row in it, which also allows a figure to be checked against
neighbouring counties.

Each census gets a data dictionary beside its tables, so the variable codes are
readable without the API documentation.

The fetch is run by hand and its output committed. `run.sh` never touches the
network, so anyone who clones this repository can build every figure with no
account, no API key and no connection.

## raw/census/ — the Census Bureau documents

Two published documents alongside the volume scans, fetched from census.gov in September
2026. They are excerpts, like the volume scans beside them.

**`population_of_states_and_counties_1790-1990_virginia_pages.pdf`** — the
title page plus the seven Virginia pages of *Population of States and Counties
of the United States: 1790-1990*. Printed page 177 carries Arlington County for
every census from 1890 to 1990; page 185 carries the Virginia notes that state
Alexandria city became independent of the county in 1900 and that the county
was renamed Arlington in 1920.

The full 236-page document is at
`www2.census.gov/library/publications/decennial/1990/population-of-states-and-counties-us-1790-1990/population-of-states-and-counties-of-the-united-states-1790-1990.pdf`
— 14.2 MB, which would have taken the repository past the 80 MB warning for
229 pages nobody needs.

**`pop-twps0076_virginia_1990.pdf`** — Census working paper POP-TWPS0076,
Virginia table, giving Arlington's 1990 population by race and Hispanic origin.
This is one of the two URLs cited inside the delivered workbook.
