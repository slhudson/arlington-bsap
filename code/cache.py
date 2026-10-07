"""A content-addressed cache for run.sh's stages and code/paper.py's compiles.

    .venv/bin/python code/cache.py key [--also <text>] <path>...
    .venv/bin/python code/cache.py restore <stage> <key>     exit 1 if there is no entry
    .venv/bin/python code/cache.py save <stage> <key> [--report <file>] <file>...
    python3 code/cache.py venv                               the venv's python, wherever it is

`key` prints the key of the files under these paths, with --also for an
input that is not a file in the tree (the key of the stage before, whose
outputs are ignored by git and so cannot be listed).

A stage's key is a hash of the bytes of its inputs, never their modification
times: a fresh worktree gives every file the time of the checkout, so a time
says nothing about whether a file changed. Two runs whose inputs are the same
bytes get the same outputs, so the second copies the first's back instead of
computing them. The entries live in the repository's .git directory, which
every worktree of a clone shares, so a merge worktree finds what a thread's
worktree built. docs/repository.md has the reasoning.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP = 8                      # entries kept per stage; older ones are deleted on save


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def store():
    """The cache directory, in the .git that every worktree of this clone shares."""
    common = Path(_git("rev-parse", "--git-common-dir").strip())
    return (common if common.is_absolute() else ROOT / common) / "build-cache"


def venv():
    """The virtualenv's directory. A worktree has no .venv of its own (it is
    gitignored), so it is looked for here first and then in the primary
    checkout, the parent of the .git every worktree shares. Nothing has to
    be linked by hand, so nothing can be forgotten."""
    primary = Path(_git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()).parent
    for base in (ROOT, primary):
        if (base / ".venv" / "bin" / "python").exists():
            return base / ".venv"
    raise SystemExit("no venv: python3 -m venv .venv && .venv/bin/pip install "
                     "pandas matplotlib openpyxl pyflakes shapely")


def environment():
    """What the outputs depend on besides the inputs: the Python and the
    installed packages. Upgrading pandas must not restore tables pandas wrote
    before."""
    site = sorted(p.name for p in venv().resolve().glob("lib/python*/site-packages/*.dist-info"))
    return "\n".join([sys.version, *site])


def files_under(paths):
    """The files git would count as part of the tree under these paths - tracked,
    or new and not ignored - so an uncommitted edit counts and a fetched scan the
    build never reads does not."""
    listed = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard",
                  "--", *paths).split("\0")
    return sorted({f for f in listed if f and (ROOT / f).is_file()})


def key(paths, also=""):
    """A hash of the names and bytes of every file under these paths, with
    the environment and anything else the caller says the outputs depend on."""
    h = hashlib.sha256()
    h.update(environment().encode())
    h.update(also.encode())
    for f in files_under(paths):
        h.update(f.encode() + b"\0")
        h.update(hashlib.sha256((ROOT / f).read_bytes()).digest())
    return h.hexdigest()[:20]


def restore(stage, k):
    """Copy a saved stage's files back to where they were saved from, and
    print what the stage printed when it ran. False, and nothing touched, if
    this stage has no entry under this key. Copied, not linked, and with a
    new modification time, so the clean stage's check that a table was
    written this run still holds."""
    entry = store() / f"{stage}-{k}"
    if not entry.is_dir():
        return False
    for src in (entry / "files").rglob("*"):
        if src.is_file():
            dest = ROOT / src.relative_to(entry / "files")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
    report = entry / "report"
    if report.exists():
        sys.stdout.write(report.read_text())
    os.utime(entry)           # most recently used, for the pruning below
    return True


def save(stage, k, files, report=None):
    """Save these files, by their paths in the repository, as this stage's
    outputs for this key, with what the stage printed. Written to a temporary
    directory and renamed into place, so two worktrees saving at once cannot
    leave half an entry."""
    root = store()
    root.mkdir(parents=True, exist_ok=True)
    entry = root / f"{stage}-{k}"
    tmp = Path(tempfile.mkdtemp(dir=root, prefix=".partial-"))
    for f in files:
        dest = tmp / "files" / Path(f).resolve().relative_to(ROOT.resolve())
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(f), dest)
    if report:
        shutil.copyfile(report, tmp / "report")
    try:
        tmp.rename(entry)
    except OSError:           # another run saved the same key first
        shutil.rmtree(tmp)
    older = sorted(root.glob(f"{stage}-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in older[KEEP:]:
        shutil.rmtree(stale, ignore_errors=True)


if __name__ == "__main__":
    command, *args = sys.argv[1:] or [""]
    if command == "venv":
        print(venv() / "bin" / "python")
    elif command == "key":
        also = ""
        if args[:1] == ["--also"]:
            also, args = args[1], args[2:]
        print(key(args, also))
    elif command == "restore":
        sys.exit(0 if restore(*args) else 1)
    elif command == "save":
        report = None
        if args[2:3] == ["--report"]:
            report, args = args[3], args[:2] + args[4:]
        save(args[0], args[1], args[2:], report)
    else:
        sys.exit(__doc__)
