"""Arlington Historical Society -> data/raw/arlington_historical_magazine/1967_officials.pdf

Run by hand; the build never touches the network (CLAUDE.md).

    .venv/bin/python code/fetch/arlington_historical_magazine.py

"County Officials in Arlington, 1870-1960" (arlhist1967officials), Arlington
Historical Magazine, October 1967: Board membership by magisterial district,
term by term, compiled from the Board's own minute books.
"""
import urllib.request

import paths

ROOT = paths.ROOT
OUT = paths.RAW / "arlington_historical_magazine" / "1967_officials.pdf"

URL = "https://arlhist.org/wp-content/uploads/2017/02/1967-7-Officials.pdf"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    if not body.startswith(b"%PDF"):
        raise SystemExit("unexpected response - not a PDF")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(body)
    print(f"  {OUT.relative_to(ROOT)}  ({len(body):,} bytes)")


if __name__ == "__main__":
    main()
