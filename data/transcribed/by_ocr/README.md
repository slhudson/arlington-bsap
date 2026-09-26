# OCR of the census volumes

Not in git. These text files are a finding aid made from the census scans,
nothing reads them, and they took 1.8MB of the 7MB of text Overleaf syncs.
Make them on a Mac:

    .venv/bin/python code/transcribe/census.py

They land in `us_census_bureau/<year>/`, one file per volume. The scans they
read come from `code/fetch/census_volumes.py`.
