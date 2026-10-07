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
silently discarding it. It also refuses before anything is exported if the
paper loads a file from a path the mirror would not carry (verify_loads). The very first push finds no such commit anywhere in
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
import posixpath
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


# The documents the mirror has to compile, from paper/ as the working directory
# (code/paper.py's SOURCES), and the folder every relative reference starts from.
DOCUMENTS = ("paper/arlington-bsap.tex", "paper/timelines/timelines.tex")
COMPILE_DIR = "paper"
GRAPHIC_EXTENSIONS = ("", ".pdf", ".png", ".jpg", ".jpeg")
# Commands whose first braced argument names a file to read, besides \input
# and \include (and any alias of TeX's own \input, found in the text).
FILE_COMMANDS = ("includepdf", "lstinputlisting", "verbatiminput", "subfile",
                 "InputIfFileExists")


def root():
    return Path(__file__).resolve().parents[1]


def mirrored(path, directory=False):
    """Whether the mirror carries this repository path (or, for a folder, the
    files in it)."""
    return (path.rstrip("/") + "/" if directory else path).startswith(ALLOWED)


def _without_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def unmirrored(files):
    """Every file the paper loads from a path the mirror does not carry.

    `files` maps each repository path to its text for a .tex file (the other
    files may map to anything). The two documents are read from DOCUMENTS and
    every file they \\input is read in turn; a reference is resolved the way
    LaTeX does, against paper/ and not against the file that makes it, and
    checked against ALLOWED. Returns (file, what it loads, the path) for each
    one the mirror would not carry, so Overleaf could not compile it - the
    Lato files were once missing from the first mirror and nothing said so
    until someone read a screenshot. A reference through a macro argument
    (\\pairfigure{name}) is covered by the folders \\graphicspath names."""
    problems, seen = [], set()
    folders, graphics = [""], []   # \\graphicspath is global: every figure is looked up in all of it
    queue = [d for d in DOCUMENTS if d in files]

    def resolve(ref):
        return posixpath.normpath(posixpath.join(COMPILE_DIR, ref.strip()))

    def found(ref, extensions):
        path = resolve(ref)
        return next((path + e for e in extensions if path + e in files), None)

    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        text = _without_comments(files[name])

        def need(what, path, directory=False):
            if not mirrored(path, directory):
                problems.append((name, what, path))

        aliases = re.findall(r"\\let\\([A-Za-z]+)\\@@input", text)
        reads = "|".join(["input", "include", *aliases])
        for m in re.finditer(r"\\(?:%s)(?![A-Za-z@])\s*(?:\{([^}]*)\}|([^\s{}\\]+))" % reads, text):
            ref = m.group(1) or m.group(2)
            path = found(ref, ("", ".tex")) or resolve(ref) + ".tex"
            need(m.group(0), path)
            if mirrored(path) and path in files:
                queue.append(path)
        for m in re.finditer(r"\\(?:%s)(?![A-Za-z@])\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}" % "|".join(FILE_COMMANDS), text):
            need(m.group(0), resolve(m.group(1)))
            if m.group(0).startswith("\\subfile") and resolve(m.group(1)) + ".tex" in files:
                queue.append(resolve(m.group(1)) + ".tex")

        for m in re.finditer(r"\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}", text):
            for d in re.findall(r"\{([^}]*)\}", m.group(1)):
                need(m.group(0), resolve(d), directory=True)
                folders.append(d)
        for m in re.finditer(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            if "#" not in m.group(1):         # a macro's argument: the folders cover it
                graphics.append((name, m.group(0), m.group(1)))
        for m in re.finditer(r"\\addbibresource\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            need(m.group(0), resolve(m.group(1)))
        for m in re.finditer(r"\\bibliography\s*\{([^}]*)\}", text):
            for b in m.group(1).split(","):
                need(m.group(0), resolve(b) + ".bib")
        for m in re.finditer(r"Path\s*=\s*([^,\]\s}]+)", text):
            need("a font's " + m.group(0), resolve(m.group(1)), directory=True)
        for m in re.finditer(r"\\(?:documentclass|usepackage|RequirePackage|LoadClass)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
            for pkg in m.group(1).split(","):
                if "/" in pkg:
                    need(m.group(0), resolve(pkg))
    for name, what, ref in graphics:
        hit = next((h for d in folders for h in [found(posixpath.join(d, ref), GRAPHIC_EXTENSIONS)] if h), None)
        if hit is None:
            problems.append((name, what, resolve(ref) + " (not in the repository)"))
        elif not mirrored(hit):
            problems.append((name, what, hit))
    return problems


def committed_files(repo):
    """The repository's paths at HEAD, with the text of each .tex file: what
    `push` would export, and never the working tree."""
    listed = git("ls-tree", "-r", "--name-only", "HEAD", cwd=repo).stdout.splitlines()
    return {f: (git("show", f"HEAD:{f}", cwd=repo).stdout if f.endswith(".tex") else "") for f in listed}


def verify_loads(repo):
    """Refuse a push when the paper loads anything the mirror would not carry."""
    problems = unmirrored(committed_files(repo))
    if problems:
        raise SystemExit(
            "the paper loads files the mirror does not carry (ALLOWED in code/publish.py), "
            "so Overleaf could not compile it:\n  "
            + "\n  ".join(f"{name}: {what} -> {path}" for name, what, path in problems))


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
    verify_loads(repo)
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
    exported = subprocess.run(["git", "archive", "HEAD", "--", *(a.rstrip("/") for a in ALLOWED)],
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
    """Apply the Overleaf mirror's commits since our last publish to a new
    branch overleaf-<date>, ready for code/merge.sh.

    The branch and its commit are made in a worktree under
    .claude/worktrees/, the way a thread's own branch is, never in the
    primary checkout: .githooks/pre-commit refuses a commit there while
    another session is live, and a pull that died mid-commit on 8 October
    2026 (mirror commits 638a1c4, bd806cb) left a staged patch and nothing
    else to show for it. A worktree's commit is exactly that worktree's own
    tree - the applied patch and nothing another session has in flight - and
    the hook does not even run there (it answers only for the primary
    checkout), so a live session cannot strand this the same way again.

    Idempotent: if overleaf-<date> already exists, this pull already
    absorbed the mirror's edit onto it, and nothing is pulled again - the
    bug this guards against ran `pull` a second time (merge.sh calls it as
    its own first step) and tried to create the same branch, which failed on
    "already exists" and stopped the merge. The branch name is dated because
    that is the grain pull already pulls at: more than one Overleaf edit
    landing on the mirror the same day lands on the one branch together,
    which is what re-running a merge on an unmerged branch has always done.
    """
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

    branch = f"overleaf-{date.today().isoformat()}"
    if git("rev-parse", "-q", "--verify", branch, cwd=repo, check=False).returncode == 0:
        print(f"pull: branch {branch} already holds the mirror's edit, merge it")
        return branch

    diff = git("diff", base, tip, "--", "paper", cwd=draft).stdout
    tree = Path(repo) / ".claude" / "worktrees" / branch
    tree.parent.mkdir(parents=True, exist_ok=True)
    git("worktree", "add", "-q", "-b", branch, str(tree), "main", cwd=repo)
    applied = subprocess.run(["git", "apply", "-"], cwd=tree, input=diff, text=True,
                              capture_output=True)
    if applied.returncode != 0:
        git("worktree", "remove", "--force", str(tree), cwd=repo, check=False)
        git("branch", "-q", "-D", branch, cwd=repo, check=False)
        raise SystemExit(f"the Overleaf edit did not apply cleanly:\n{applied.stderr}")
    git("add", "-A", cwd=tree)
    span = f"{base[:7] if last else 'project start'}..{tip[:7]}"
    git("commit", "-q", "-m", f"Overleaf edit: {span}", cwd=tree)
    git("worktree", "remove", str(tree), cwd=repo)
    print(f"pull: branch {branch}, ready for bash code/merge.sh {branch}")
    return branch


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("push", "pull"):
        raise SystemExit("usage: .venv/bin/python code/publish.py push|pull")
    {"push": push, "pull": pull}[sys.argv[1]]()
