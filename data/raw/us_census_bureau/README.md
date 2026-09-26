# Census volumes not kept in git

Six scans the build never reads are not in this repository, because together
they are 50MB and would push Overleaf past its ceiling. `data/contents.csv` has
each one's URL and checksum. To fetch them, refusing any byte that differs:

    .venv/bin/python code/fetch/census_volumes.py

The six:

- `1880/1880_v1-12.pdf`
- `1880/1880_v1-13.pdf`
- `1890/1890a_v1-11.pdf`
- `1890/1890a_v1-12.pdf`
- `1890/1890a_v1-13.pdf`
- `1890/1890a_v1-14.pdf`

The scans that are in git are the title-page chunks and the tables the
transcriptions were read from. Nothing here is edited.
