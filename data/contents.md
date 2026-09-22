# Contents of data/

Four layers, ordered by how much they can be trusted. Which folder something
belongs in is decided by how the numbers got there, not by what they are about.

| Folder | What it holds | Who reads it |
|---|---|---|
| `raw/` | published sources, as they exist in the world | `build/` |
| `extracted/` | machine-derived from `raw/` — **not trusted** | people only |
| `manual/` | hand-keyed by a person | `build/` |
| `clean/` | built from `raw/` and `manual/` | `analysis/` |

A file in `raw/` is its own citation: the volume is the evidence. A file in
`manual/` is not — someone read something and typed a number, so it needs a
citation per cell. That difference is the whole of the sourcing problem, and
`docs/sources.md` tracks it.

`extracted/` is absent from `build/files.py` and `analysis/files.py` by design.
OCR misreads digits, so the only way out of that folder is a person reading the
scan and typing the number into `manual/`.

---

## raw/census/

Extracts from the published 1870, 1880 and 1890 decennial census volumes,
gathered by Alex Keena in September 2026 while correcting the 1870–1890 county
population figures. Received 2026-09-22. Nothing here should ever change; the
checksums are so that a change would be noticed.

Where exactly they came from is not recorded. The filenames match how the
Census Bureau chunks its scanned volumes, but that is an inference — see
`docs/questions.md` Q8.

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

## extracted/census/

OCR of all 521 pages, one text file per volume, produced by
`build/ocr_census.py` using macOS Vision. Not part of `bash run.sh` — it takes
about twelve minutes and its input never changes.

Use it to find a table and a page. Do not read numbers from it: OCR of
19th-century tables misreads digits routinely, and the text layer already
embedded in the 1880 files renders 13,659 as `lB, 659`.

## manual/

Assembled by Alex Keena, received 2026-09-22.

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
