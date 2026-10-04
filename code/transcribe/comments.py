"""The County's public correspondence on the form of government -> data/transcribed/by_claude/comments.csv

Run by hand, output committed.

    .venv/bin/pip install extract_msg
    .venv/bin/python code/transcribe/comments.py

The County shared the correspondence its Board received with the whole study
team: 250 Outlook messages in three folders of the project's Drive, 180MB in
all. None of it is in data/raw/ and none of it will be. The repository is
meant to go public, the messages carry residents' names, addresses and
signature blocks, and a permanent indexed archive of them is a different
object from the County's own file, whatever each letter's status under FOIA
(docs/comments.md).

What this writes instead is an index: one row per message, carrying what a
count needs and nothing a person could be found by. No name, no address, no
message body. A writer is a number, assigned in the order the messages sort,
so the same person is the same number and the mapping back exists only
beside the messages themselves.

The National Civic League coded these for its part of the report and reports
218 comments from roughly 156 commenters. Neither number falls out of this
folder on any rule this script can apply, so `file` holds the County's own
path to each message: it is what their coding has to join on.

    comment     this index's id for the message
    file        its path under the County's folder, the join key
    batch       which of the County's folders it came from
    date        when it was sent
    subject     the subject line
    writer      the sender, as a number
    from_county whether that sender is a County address, which marks a
                message staff forwarded rather than one a resident sent
    forwarded   whether the body quotes a From: header, so the resident who
                wrote it may be inside the message rather than its sender
    duplicate_of  the first message carrying the same body, where one does
"""
import csv
import hashlib
import pathlib
import re

import extract_msg

from paths import BY_CLAUDE

SHARED = pathlib.Path.home() / (
    "Library/CloudStorage/GoogleDrive-sally@rankedchoiceva.org/"
    ".shortcut-targets-by-id/1M4kZqG-XFRNQ9jele3PcD6mfZog7E5_Q/RCVa/research/"
    "Virginia/Arlington/2026 - Form of Government/team/sources/CBO")
OUT = BY_CLAUDE / "comments.csv"
COUNTY = "arlingtonva.us"

FIELDS = ["comment", "file", "batch", "date", "subject", "writer",
          "from_county", "forwarded", "duplicate_of"]


def address(sender: str) -> str:
    """The address in a sender header, which Outlook writes either bare or
    as `Name <addr>`; the whole string lowered where it carries none."""
    found = re.findall(r"[\w.+-]+@[\w.-]+", sender or "")
    return (found[-1] if found else (sender or "")).lower().strip()


def body_key(body: str) -> str:
    """A message's body as one key, whitespace flattened and case dropped,
    so the same letter filed twice is recognised. Only the key is kept."""
    return hashlib.sha256(re.sub(r"\s+", " ", body or "").strip().lower()
                          [:4000].encode()).hexdigest()[:12]


def read(path):
    message = extract_msg.Message(path)
    try:
        return {"date": str(message.date or "")[:10],
                "subject": (message.subject or "").strip(),
                "sender": address(message.sender),
                "body": message.body or ""}
    finally:
        message.close()


def index() -> list:
    if not SHARED.exists():
        raise SystemExit(
            f"the County's shared folder is not on this machine:\n  {SHARED}\n"
            f"It is not in the repository and will not be (see the docstring). "
            f"The output of this step is committed, so nothing else needs it.")
    files = sorted(SHARED.rglob("*.msg"), key=lambda p: str(p).lower())
    if not files:
        raise SystemExit(f"no .msg files under {SHARED}")

    writers, bodies, rows = {}, {}, []
    for n, path in enumerate(files, 1):
        m = read(path)
        writers.setdefault(m["sender"], f"w{len(writers) + 1:03d}")
        key = body_key(m["body"])
        comment = f"c{n:03d}"
        rows.append({
            "comment": comment,
            "file": str(path.relative_to(SHARED)),
            "batch": path.relative_to(SHARED).parts[0],
            "date": m["date"],
            "subject": m["subject"],
            "writer": writers[m["sender"]],
            "from_county": str(m["sender"].endswith(COUNTY)).lower(),
            "forwarded": str(bool(re.search(r"^\s*From:", m["body"], re.M))).lower(),
            "duplicate_of": bodies.get(key, ""),
        })
        bodies.setdefault(key, comment)
    return rows


if __name__ == "__main__":
    rows = index()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    first = [r for r in rows if not r["duplicate_of"]]
    print(f"  {OUT.name:<22} {len(rows):>4} messages, {len(first)} distinct, "
          f"{len({r['writer'] for r in rows})} senders")
