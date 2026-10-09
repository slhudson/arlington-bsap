"""Read the County's comment messages without printing a resident.

    ARLINGTON_CORRESPONDENCE=/path/to/the/Drive/folder .venv/bin/python code/sources/county_messages.py
    ... county_messages.py c017                      # one message: its fields, no values
    ... county_messages.py c017 --show-resident-field body

The 250 Outlook messages carry residents' names, phones and home addresses
in their senders, subjects, bodies and signature blocks (docs/comments.md).
A session that read them printed those into its output three times, so this
is the one way to look at them: what comes out is counts, file names and the
names of fields. A field that holds what a resident wrote - `sender`,
`subject`, `body` - prints only when it is named with
`--show-resident-field`, one at a time, and the message it is read from is
named too. `render()` refuses to print one without that, so a caller cannot
forget.

Needs `extract_msg` (`.venv/bin/pip install extract_msg`), imported when a
message is read so the rest of the module runs without it.
"""
import argparse
import os
import pathlib
import re

# What a message offers and what is safe to print of it. A value of a safe
# field says nothing about who wrote the message; a resident field is what
# they wrote or who they are.
SAFE_FIELDS = {"date": lambda m: m["date"],
               "from_county": lambda m: str(m["sender"].endswith("arlingtonva.us")).lower(),
               "forwarded": lambda m: str(bool(re.search(r"^\s*From:", m["body"], re.M))).lower(),
               "body_characters": lambda m: str(len(m["body"]))}
RESIDENT_FIELDS = ("sender", "subject", "body")


def read(path):
    """One message as a dict of the fields above. The only place a message
    is opened."""
    import extract_msg
    message = extract_msg.Message(path)
    try:
        sender = message.sender or ""
        found = re.findall(r"[\w.+-]+@[\w.-]+", sender)
        return {"date": str(message.date or "")[:10],
                "subject": (message.subject or "").strip(),
                "sender": (found[-1] if found else sender).lower().strip(),
                "body": message.body or ""}
    finally:
        message.close()


def render(message, show=()):
    """One message as lines of `field: value`. Safe fields carry their
    values; a resident field carries only its name unless it is in `show`.
    `show` naming something that is not a field is an error, not a no-op."""
    unknown = set(show) - set(RESIDENT_FIELDS)
    if unknown:
        raise ValueError(f"not a resident field: {sorted(unknown)}; one of {RESIDENT_FIELDS}")
    lines = [f"{name}: {get(message)}" for name, get in SAFE_FIELDS.items()]
    for name in RESIDENT_FIELDS:
        lines.append(f"{name}: {message[name]}" if name in show
                     else f"{name}: (resident field; --show-resident-field {name} to print)")
    return "\n".join(lines)


def summary(counts):
    """`counts` is {folder: number of messages}; the lines that report them."""
    lines = [f"{n:>4}  {folder}" for folder, n in sorted(counts.items())]
    lines.append(f"{sum(counts.values()):>4}  messages")
    lines.append("fields: " + ", ".join([*SAFE_FIELDS, *RESIDENT_FIELDS]))
    return "\n".join(lines)


def folder():
    path = os.environ.get("ARLINGTON_CORRESPONDENCE")
    if not path or not pathlib.Path(path).exists():
        raise SystemExit("set ARLINGTON_CORRESPONDENCE to the County's shared folder "
                         "on this machine (docs/setup.md)")
    return pathlib.Path(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("comment", nargs="?",
                    help="a comment id from data/transcribed/by_claude/comments.csv (c017)")
    ap.add_argument("--show-resident-field", action="append", default=[],
                    choices=RESIDENT_FIELDS, dest="show",
                    help="print this field of the named message; one flag per field")
    args = ap.parse_args()
    root = folder()
    files = sorted(root.rglob("*.msg"), key=lambda p: str(p).lower())
    if args.comment is None:
        if args.show:
            raise SystemExit("--show-resident-field needs the comment id it is read from")
        counts = {}
        for f in files:
            counts[f.relative_to(root).parts[0]] = counts.get(f.relative_to(root).parts[0], 0) + 1
        print(summary(counts))
    else:
        # The same numbering as code/transcribe/comments.py: c001 is the
        # first message in the sorted order.
        n = int(args.comment.lstrip("c"))
        if not 1 <= n <= len(files):
            raise SystemExit(f"{args.comment} is not one of the {len(files)} messages")
        print(f"{args.comment}: {files[n - 1].relative_to(root)}")
        print(render(read(files[n - 1]), args.show))
