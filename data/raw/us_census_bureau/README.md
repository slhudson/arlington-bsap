# Census volumes not kept in git

Sixteen scans the build never reads are not in this repository, because together
they are 175MB and would push Overleaf past its ceiling. `data/contents.csv`
has each one's URL and checksum. To fetch them, refusing any byte that differs:

    .venv/bin/python code/fetch/census_volumes.py

The 1880 and 1890 interior chunks, which hold the tables the county totals
and race counts were read from:

- `1880/1880_v1-12.pdf`
- `1880/1880_v1-13.pdf`
- `1890/1890a_v1-11.pdf`
- `1890/1890a_v1-12.pdf`
- `1890/1890a_v1-13.pdf`
- `1890/1890a_v1-14.pdf`

The 1930-1970 volumes' front matter, on which each bibliography entry rests,
and the chapter holding Arlington's age tables:

- `1930/10612982v3p2.pdf`, `1930/10612982v3p2ch10.pdf`
- `1940/33973538v2p7.pdf`, `1940/33973538v2p7ch3.pdf`
- `1950/37784122v2p46.pdf`, `1950/37784122v2p46ch3.pdf`
- `1960/09768066v1p48.pdf`, `1960/09768066v1p48ch3.pdf`
- `1970/00496492v1p48.pdf`, `1970/00496492v1p48ch03.pdf`

The scans that are in git are the 1870 chunks and the 1880 and 1890
title-page chunks. Nothing here is edited.
