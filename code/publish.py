"""Publish paper/ and figures/pdf/ (and style/fonts/) to the Overleaf mirror, and bring an
Overleaf edit back. Outside the five stages, like code/merge.sh (CLAUDE.md,
docs/repository.md).

    .venv/bin/python code/publish.py push
    .venv/bin/python code/publish.py pull

Two repositories hold this project: the whole one, where the five stages and
the threads work, and arlington-bsap-draft, which Overleaf is linked to and
syncs nothing else. `push` rebuilds the mirror's tree as exactly paper/,
figures/pdf/ and style/fonts/ (the Lato files the paper loads) from this repository's HEAD, committed on the mirror as
"main <hash>: <subject>" - a commit on top of the mirror's own history, never
a rewrite of it, so Overleaf keeps its common ancestor. That message is also
how the next push recognises its own work: if the mirror's tip is not one of
these commits, something landed there since the last publish - an edit made
in Overleaf - and the push refuses, naming the pull command instead of
silently discarding it. The very first push finds no such commit anywhere in
the mirror's history and runs unconditionally: on a mirror nobody has pushed
to, as a root commit pushed as main.

`pull` reads the mirror's commits back to the last one of ours - Overleaf's
own edits - and applies the changes they made under paper/ to a new branch
overleaf-<date> here, ready for `bash code/merge.sh overleaf-<date>`. A
change under figures/ is refused outright: figures are built here, never
hand-edited on either side.

git subtree publishes one prefix of a repository to a second remote; this
mirror holds two sibling prefixes (paper/, figures/pdf/), not one, which
subtree has no way to express as a single split. Plain plumbing - export the
two trees from HEAD, graft them under the mirror's root, commit, push - says
the same thing in less code and keeps the whole operation in one place to
read.

The mirror's own checkout lives at .git/draft-checkout, beside the build
cache (code/cache.py): never in the working tree, so the two repositories'
files never mix, and persistent, so a push can read what it wrote last time
without the working tree carrying any trace of the mirror.
"""
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

PUBLISHED = re.compile(r"^main ([0-9a-f]+): ")
# paper/ and the figures it includes, and the typeface it loads from
# ../style/fonts/: without them the mirror cannot compile by itself.
ALLOWED = ("paper/", "figures/pdf/", "style/fonts/")


def root():
    return Path(__file__).resolve().parents[1]


def git(*args, cwd, check=True):
    return subprocess.run(["git", "-C", str(cwd), *args], check=check,
                           capture_output=True, text=True)


def draft_url(repo):
    """arlington-bsap-draft, at the same host and owner as `repo`'s origin.
    DRAFT_REMOTE overrides this, the way code/merge.sh's REMOTE does, so a
    test can point it at a throwaway repository."""
    override = os.environ.get("DRAFT_REMOTE")
    if override:
        return override
    origin = git("remote", "get-url", "origin", cwd=repo, check=True).stdout.strip()
    url, n = re.subn(r"/arlington-bsap(\.git)?$", r"/arlington-bsap-draft\1", origin)
    if n != 1:
        raise SystemExit(f"origin does not name arlington-bsap, cannot find the mirror: {origin}")
    return url


def draft_checkout(repo):
    """The mirror's own checkout: cloned here on first use, then just
    fetched and reset to the mirror's current main. Living at .git/ means
    every worktree of this clone shares it (code/cache.py's reasoning
    exactly), so any of them can push or pull and see what the last one did."""
    common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir",
                       cwd=repo).stdout.strip())
    draft = common / "draft-checkout"
    if not draft.exists():
        subprocess.run(["git", "clone", "-q", draft_url(repo), str(draft)],
                        check=True, capture_output=True, text=True)
        git("config", "user.email", "publish@arlington-bsap.local", cwd=draft)
        git("config", "user.name", "code/publish.py", cwd=draft)
    git("fetch", "-q", "origin", cwd=draft)
    if git("rev-parse", "--verify", "-q", "origin/main", cwd=draft, check=False).returncode == 0:
        git("checkout", "-q", "-B", "main", "origin/main", cwd=draft)
    else:
        # A mirror nobody has pushed to has no main. Point at an unborn main,
        # so the first publish is a root commit pushed as main.
        git("update-ref", "-d", "refs/heads/main", cwd=draft, check=False)
        git("symbolic-ref", "HEAD", "refs/heads/main", cwd=draft)
    return draft


def last_published(draft):
    """(sha, at_tip): the most recent commit of ours in the mirror's
    history, walking back from its tip, and whether the tip itself is that
    commit - meaning nothing has landed there since. (None, False) if we
    have never published to this mirror."""
    # An empty mirror has no commits to walk.
    log = git("log", "--format=%H %s", "main", cwd=draft, check=False).stdout.splitlines()
    for i, line in enumerate(log):
        sha, _, subject = line.partition(" ")
        if PUBLISHED.match(subject):
            return sha, i == 0
    return None, False


def verify_tree(draft):
    """Every path the mirror would commit is under paper/, figures/pdf/ or style/fonts/ -
    the invariant the whole design rests on, checked once more right before
    the commit that would ship a violation."""
    tracked = git("ls-files", cwd=draft).stdout.splitlines()
    bad = [f for f in tracked if not f.startswith(ALLOWED)]
    if bad:
        raise SystemExit(
            "the mirror's tree holds paths outside paper/, figures/pdf/ and style/fonts/, refusing to commit:\n  "
            + "\n  ".join(bad))


def push(repo=None):
    repo = repo or root()
    draft = draft_checkout(repo)
    last, at_tip = last_published(draft)
    if last is not None and not at_tip:
        raise SystemExit(
            "the mirror has commits main has not absorbed - an edit made in Overleaf:\n"
            "  .venv/bin/python code/publish.py pull")

    subject = git("log", "-1", "--format=%s", "HEAD", cwd=repo).stdout.strip()
    short = git("rev-parse", "--short", "HEAD", cwd=repo).stdout.strip()

    # The mirror's tree becomes exactly paper/ and figures/pdf/ from HEAD:
    # everything else removed first, then the two folders exported from the
    # committed tree (never the working tree, so an uncommitted edit here
    # cannot reach Overleaf) and laid back down at the same paths.
    for entry in draft.iterdir():
        if entry.name == ".git":
            continue
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    exported = subprocess.run(["git", "archive", "HEAD", "--", "paper", "figures/pdf", "style/fonts"],
                               cwd=repo, check=True, capture_output=True)
    subprocess.run(["tar", "-x", "-C", str(draft)], input=exported.stdout, check=True)

    git("add", "-A", cwd=draft)
    verify_tree(draft)
    if not git("status", "--porcelain", cwd=draft).stdout.strip():
        print("push: nothing changed since the last publish")
        return
    git("commit", "-q", "-m", f"main {short}: {subject}", cwd=draft)
    git("push", "-q", "origin", "main", cwd=draft)
    head = git("rev-parse", "--short", "HEAD", cwd=draft).stdout.strip()
    print(f"push: {draft_url(repo)} main -> {head}")
    return head


def pull(repo=None):
    repo = repo or root()
    draft = draft_checkout(repo)
    last, at_tip = last_published(draft)
    if last is None:
        # Nothing has ever been published, so there is no baseline to read
        # Overleaf's edits against.
        print("pull: nothing to pull; the mirror has not been published to yet")
        return None
    if at_tip:
        print("pull: nothing to pull; the mirror has no commits since the last publish")
        return None

    base = last
    tip = git("rev-parse", "main", cwd=draft).stdout.strip()
    changed = git("diff", "--name-only", base, tip, cwd=draft).stdout.split()
    if not changed:
        print("pull: nothing changed under paper/")
        return None
    outside = [f for f in changed if not f.startswith("paper/")]
    if outside:
        raise SystemExit(
            "only paper/ comes back from Overleaf (figures are built here, fonts are not edited); refusing a pull that touches:\n  "
            + "\n  ".join(outside))

    diff = git("diff", base, tip, "--", "paper", cwd=draft).stdout
    branch = f"overleaf-{date.today().isoformat()}"
    git("checkout", "-q", "-b", branch, "main", cwd=repo)
    applied = subprocess.run(["git", "apply", "-"], cwd=repo, input=diff, text=True,
                              capture_output=True)
    if applied.returncode != 0:
        git("checkout", "-q", "main", cwd=repo)
        git("branch", "-q", "-D", branch, cwd=repo)
        raise SystemExit(f"the Overleaf edit did not apply cleanly:\n{applied.stderr}")
    git("add", "-A", cwd=repo)
    span = f"{base[:7] if last else 'project start'}..{tip[:7]}"
    git("commit", "-q", "-m", f"Overleaf edit: {span}", cwd=repo)
    print(f"pull: branch {branch}, ready for bash code/merge.sh {branch}")
    return branch


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("push", "pull"):
        raise SystemExit("usage: .venv/bin/python code/publish.py push|pull")
    {"push": push, "pull": pull}[sys.argv[1]]()
