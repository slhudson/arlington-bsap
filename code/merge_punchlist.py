"""After a merge: take back out of docs/punchlist.md the lines the branch deleted.

    python3 code/merge_punchlist.py <worktree> <base> <branch>

docs/punchlist.md merges by union (.gitattributes), so that two sessions
appending to it never conflict. The cost is that when one side deletes a
line and the other adds a line beside it, git sees one disputed hunk and
keeps both sides of it: the deleted line comes back, and a cleared item is
open again. code/merge.sh runs this on the merged tree. `base` is where the
branch left main, `branch` the incoming side; every line the branch removed
that the merged file still holds is removed, and each is printed so the
merge's log names it.
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

FILE = "docs/punchlist.md"


def drop_deleted(base, theirs, merged):
    """(merged text without the lines `theirs` deleted from `base`, those
    lines). Counted, not set-based: a line that was in `base` twice and is
    in `theirs` once was deleted once. A line is dropped only up to the
    number of times it is in `merged` beyond what `theirs` holds, so a line
    the branch kept is never touched."""
    deleted = Counter(base.splitlines()) - Counter(theirs.splitlines())
    deleted.pop("", None)                       # blank lines are layout, not items
    over = Counter(merged.splitlines()) - Counter(theirs.splitlines())
    owed = {line: min(n, over[line]) for line, n in deleted.items() if over[line]}
    kept, removed = [], []
    for line in merged.splitlines():
        if owed.get(line):
            owed[line] -= 1
            removed.append(line)
        else:
            kept.append(line)
    return "\n".join(kept) + ("\n" if merged.endswith("\n") else ""), removed


def show(tree, ref):
    """The file at a ref, or empty where the ref does not hold it."""
    found = subprocess.run(["git", "-C", tree, "show", f"{ref}:{FILE}"],
                           capture_output=True, text=True)
    return found.stdout if found.returncode == 0 else ""


if __name__ == "__main__":
    tree, base, branch = sys.argv[1:4]
    path = Path(tree) / FILE
    if path.exists():
        text, removed = drop_deleted(show(tree, base), show(tree, branch), path.read_text())
        if removed:
            path.write_text(text)
            for line in removed:
                print(f"   {FILE}: {branch} deleted this line, the union merge brought it back, removed: {line}")
