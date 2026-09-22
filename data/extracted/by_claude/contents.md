# by_claude/

Tables I read off rendered page images, one file per source table, laid out as
the table is printed rather than reshaped into whatever a script wanted.

**This is a machine's reading, not a person's.** A vision model reading a page
image is better than OCR and wrong in different ways. Nothing here is confirmed
until it appears in `by_human/`.

## Why table-shaped

Transcribing the whole table, in its own structure, means it can be checked
against the page as a whole — a reader can see whether a row is missing or a
column is misaligned, which a list of extracted values hides.

## The `level` column

`level` records the printed indentation. Level 0 is the table's own total,
level 1 its parts, level 2 a detail of the line above.

This exists because of a specific error. In Table 5, Freedman village is
printed at level 2 beneath "Arlington district, including Freedman village" at
level 1 — its residents are already inside that district. Treating it as a
fourth district adds them twice. With the level recorded, code can refuse to
sum a child alongside its parent, so the mistake cannot be made rather than
merely being warned against.

## Files

Named `<volume>_p<printed page>_table<n>_<state>_<subject>.csv`, so the
citation is the filename.

| File | What it gives |
|---|---|
| `1870a-04_p69_table2_...` | Alexandria County by race, 1870 back to 1800 |
| `1870a-09_p278_table3_...` | Alexandria city and its wards by race, 1870 |
| `1880_v1-13_p412_table5_...` | Alexandria County by race, 1880/1870/1860 |
| `1880_v1-13_p425_table6_...` | Alexandria city by race, 1880 and 1870 |
| `1890a_v1-11_p346_table5_...` | County, city, wards and districts, 1890 and 1880 |
| `1890a_v1-14_p520_table22_...` | Alexandria County by race and sex, 1890 |
| `1890a_v1-14_p556_table23_...` | Alexandria city by race and sex, 1890 |

Values read twice from different volumes agree: the 1870 county and city race
figures appear in both the 1870 and 1880 volumes.
