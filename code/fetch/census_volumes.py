"""Census volume front matter -> data/raw/us_census_bureau/<year>/<volume>-01.pdf

NOT part of `bash run.sh`. Like the rest of code/fetch/, it touches the network
and its output is committed, so the build stays reproducible without it.

    .venv/bin/python code/fetch/census_volumes.py

**Why this exists.** The 1880 and 1890 scans in data/raw/ are interior chunks:
open one and it starts partway into a table of Oregon townships. No cover, no
title page, nothing saying which volume it is. So the bibliography could not
say what it was citing, and said so - the entries were marked provisional and
their titles inferred from the filenames.

The Bureau chunks each volume the same way and publishes the pieces under those
same names, first chunk first. This fetches the first chunk, which carries the
title page and the letter of transmittal, and saves it beside the chunks
already held.

**The filename is not the evidence; the checksum is.** Each chunk already in
data/raw/ is compared byte for byte against the Bureau's copy at the URL below.
Matching proves the held files are that volume rather than merely named like
it. Both matched on 23 September 2026. A mismatch stops the script: it would
mean the volume was reorganised, or that the files came from somewhere else
after all, and either is worth knowing before a citation rests on it.
"""
import hashlib
import urllib.request

import paths

ROOT = paths.ROOT
RAW = paths.RAW / "us_census_bureau"
BASE = "https://www2.census.gov/library/publications/decennial"

# year: (directory on census.gov, front-matter chunk, a chunk already held)
VOLUMES = {
    "1880": ("1880/vol-01-population", "1880_v1-01.pdf", "1880_v1-12.pdf"),
    "1890": ("1890/volume-1", "1890a_v1-01.pdf", "1890a_v1-11.pdf"),
}


def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read()


def digest(b):
    return hashlib.sha256(b).hexdigest()


def main():
    for year, (directory, front, witness) in VOLUMES.items():
        held = RAW / year / witness
        if not held.exists():
            raise FileNotFoundError(f"{held} missing - nothing to check the volume against")

        remote = fetch(f"{BASE}/{directory}/{witness}")
        if digest(remote) != digest(held.read_bytes()):
            raise AssertionError(
                f"{witness} differs from {BASE}/{directory}/{witness}. The held "
                f"file is not the Bureau's copy of that chunk, so the volume it "
                f"belongs to is not established. Do not cite it as this volume "
                f"until that is resolved.")
        print(f"  {witness:<20} matches the Bureau's copy")

        out = RAW / year / front
        out.write_bytes(fetch(f"{BASE}/{directory}/{front}"))
        print(f"  {front:<20} {out.stat().st_size // 1024:>6} KB  <- {directory}")


if __name__ == "__main__":
    main()
