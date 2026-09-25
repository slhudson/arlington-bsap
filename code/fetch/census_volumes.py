"""Census volume scans -> data/raw/us_census_bureau/<year>/<chunk>.pdf, on demand.

    .venv/bin/python code/fetch/census_volumes.py

The 1880 and 1890 volumes' interior chunks are 50MB of PDF the build never
opens, so they are not committed: data/contents.csv records each one's URL
and checksum with `in_git = no`, and this fetches whichever is missing. A
download whose checksum does not match the inventory is refused, since it
is then not the file the transcriptions were read from. Every chunk on
disk is checked against the inventory too, so on a full checkout this is a
provenance audit that downloads nothing. The title-page chunks and the
1870 chunks are committed (1870-chunks-provenance in docs/questions.csv).
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
