"""Census volume scans -> data/raw/us_census_bureau/<year>/<chunk>.pdf, on demand.

NOT part of `bash run.sh`. Like the rest of code/fetch/, it touches the
network. The build never reads a scan - it reads the transcriptions, which
cite the printed page - so nothing here is needed to build.

    .venv/bin/python code/fetch/census_volumes.py

**Why some scans are not committed.** The 1880 and 1890 volumes' interior
chunks are 50MB of PDF the build never opens, against an Overleaf ceiling of
100MB for the whole repository. They are the Bureau's own files, published at
stable URLs and byte-identical to what was held, so `data/contents.csv`
records each one's URL and checksum and marks it `in_git = no`, and this
script fetches whichever is missing. A download whose checksum does not match
the inventory is refused and not written: the file is then not the one the
transcriptions were read from, and that is worth knowing before anyone cites
a page of it.

The title-page chunks are committed, because `paper/sources.bib` is built
from them. So are the three 1870 chunks: the Bureau's current copies at
1870/population/ are chunked differently, so those files cannot be re-fetched
(`1870-chunks-provenance` in `docs/questions.csv`).

Every chunk already on disk is checked against the inventory too, so running
this on a full checkout is a provenance audit that downloads nothing.
"""
import csv
import hashlib
import urllib.request

import paths

INVENTORY = paths.ROOT / "data" / "contents.csv"


def fetch(url):
    with urllib.request.urlopen(url, timeout=600) as r:
        return r.read()


def digest(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    rows = [r for r in csv.DictReader(INVENTORY.open()) if r["layer"] == "raw" and r["url"]]
    for r in rows:
        path = paths.ROOT / r["path"]
        if path.exists():
            got = digest(path.read_bytes())
            if got != r["sha256"]:
                raise AssertionError(
                    f"{r['path']} does not match the checksum in {INVENTORY.name} "
                    f"({got} against {r['sha256']}). data/raw/ is never edited; find out what changed.")
            print(f"  {path.name:<20} on disk, matches the inventory")
            continue
        body = fetch(r["url"])
        got = digest(body)
        if got != r["sha256"]:
            raise AssertionError(
                f"{path.name}: the Bureau's copy at {r['url']} has checksum {got}, and the "
                f"inventory says {r['sha256']}. Not written - it is not the file the "
                f"transcriptions were read from. Do not cite it until that is resolved.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        print(f"  {path.name:<20} {len(body) // 1024:>6} KB  fetched and verified  <- {r['url']}")


if __name__ == "__main__":
    main()
