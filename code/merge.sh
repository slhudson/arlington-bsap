#!/usr/bin/env bash
# Merge a thread's branch into main, the way it was done by hand six times on
# 5 October 2026, with the places to slip taken out of a person's hands.
#
#   bash code/merge.sh <branch>
#
# One line per step. The steps, in order, and what each one refuses:
#
#   1. The Overleaf mirror checked for an edit to pull back
#      (code/publish.py pull). If there is one, it is already sitting on its
#      own branch by the time this prints - a person reviews and merges it
#      like any other thread's, which is what it now is - and this run stops
#      before touching the branch it was asked to merge.
#   2. A scratch worktree on origin/main, after a fetch, so the merge is made
#      against what is pushed and not against a stale local main.
#   3. The branch merged. A conflict stops it: docs/questions.csv merges row
#      by row (code/merge_questions.py), docs/punchlist.md and the negatives
#      file by union (.gitattributes), so anything still conflicting is two
#      sessions editing one line or one row, which is a person's decision.
#      The worktree is removed and nothing has changed.
#   4. bash run.sh, then code/paper.py all, in the
#      worktree. A failure stops it before anything reaches main: a commit
#      chained after a failing build was the first of the slips.
#   5. What the build rewrote (figures/, data/clean/, the .tex files the
#      analysis stage writes) committed in the worktree, so a figure rebuilt
#      there is not lost when the worktree goes - the third slip.
#   6. main fast-forwarded to the merge and pushed; the compiled PDF copied
#      to the primary checkout; the branch removed on origin. The scratch
#      worktree goes in the EXIT trap, on success and on failure alike. The
#      thread's own worktree and local branch go only if its branch is merged
#      into main, its tree is clean, and no live session holds it
#      (`git worktree lock`): two threads lost their worktrees on 6 October
#      2026 to a cleanup that asked none of the three.
#   7. The Overleaf mirror published (code/publish.py push), so the paper and
#      figures a thread just landed reach Overleaf without a separate step
#      for anyone to remember.
#
# The build and the compile are the commands BUILD and COMPILE below;
# code/tests.py substitutes them to prove the script stops when either fails
# and goes on when both pass. Nothing else overrides them, and the remote is
# always origin.
set -euo pipefail

usage() { echo "usage: bash code/merge.sh <branch>" >&2; exit 2; }
[ $# -eq 1 ] || usage
branch=$1

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
BUILD=${BUILD:-"bash run.sh"}
COMPILE=${COMPILE:-"$ROOT/.venv/bin/python code/paper.py all"}
PYTHON=${PYTHON:-".venv/bin/python"}
REMOTE=origin

step() { printf '%s\n' "$*"; }
fail() { printf 'stopped: %s\n' "$*" >&2; exit 1; }

# The primary checkout must be on main and have nothing staged or modified in
# the files the merge will move, or the fast-forward at the end cannot land.
# Checking "clean" is the simplest form of that and the one a reader expects.
if [ "$(git rev-parse --git-dir)" != ".git" ]; then
  primary=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
  fail "this is a worktree; the merge runs from the primary checkout:
  cd $primary && bash code/merge.sh $branch"
fi
[ "$(git branch --show-current)" = "main" ] || fail "the primary checkout is on $(git branch --show-current), not main"
[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "the primary checkout has uncommitted changes; commit or stash them first"

[ "$(git config merge.questions.driver 2>/dev/null)" = "python3 code/merge_questions.py %O %A %B" ] \
  || fail "the tracker merge driver is not registered; bash run.sh installs it"

step "1. checking the Overleaf mirror for an edit to pull back"
pulled=$("$PYTHON" code/publish.py pull)
step "   $pulled"
case "$pulled" in
  "pull: branch "*)
    waiting=$(printf '%s' "$pulled" | sed -n 's/^pull: branch \([^,]*\),.*/\1/p')
    fail "an edit from Overleaf is waiting on $waiting; merge it first:
  bash code/merge.sh $waiting"
    ;;
esac

git fetch -q "$REMOTE" main
git rev-parse -q --verify "$branch" >/dev/null 2>&1 || git fetch -q "$REMOTE" "$branch:$branch" 2>/dev/null \
  || fail "no branch $branch here or on $REMOTE"
[ "$(git merge-base --is-ancestor "$REMOTE/main" main && echo yes)" = yes ] \
  || fail "local main is behind $REMOTE/main; pull first"
[ "$(git rev-parse main)" = "$(git rev-parse "$REMOTE/main")" ] \
  || fail "local main has commits $REMOTE/main does not; push them first"

name=merge-$(echo "$branch" | tr '/' '-')
tree=.claude/worktrees/$name
# The scratch worktree is this script's own, so it goes whatever happened.
cleanup() {
  git worktree remove --force "$tree" >/dev/null 2>&1 || true
  git branch -D -q "$name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# The worktree holding a thread's branch belongs to the thread, not to this
# script: say why it stays, or remove it and the local branch.
retire() {
  local path
  path=$(git worktree list --porcelain | awk -v b="refs/heads/$1" '
    /^worktree /{p=substr($0,10)} /^branch /{if($2==b)print p}')
  if [ -n "$path" ]; then
    if git worktree list --porcelain | awk -v p="$path" '
        /^worktree /{cur=substr($0,10)} /^locked/{if(cur==p)f=1} END{exit !f}'; then
      step "   kept $path: a live session holds it (locked)"; return
    fi
    [ -z "$(git -C "$path" status --porcelain)" ] || { step "   kept $path: its tree is not clean"; return; }
    git worktree remove "$path"
  fi
  git branch -D -q "$1" 2>/dev/null || true
}

step "2. worktree $tree on $REMOTE/main ($(git rev-parse --short "$REMOTE/main"))"
mkdir -p .claude/worktrees
git worktree add -q "$tree" -b "$name" "$REMOTE/main"

step "3. merge $branch ($(git rev-parse --short "$branch"))"
if ! git -C "$tree" merge -q -m "merge $branch" "$branch" >/dev/null 2>&1; then
  conflicts=$(git -C "$tree" diff --name-only --diff-filter=U)
  git -C "$tree" merge --abort 2>/dev/null || true
  fail "conflicts a person has to resolve, outside the union-merged files:
$(printf '  %s\n' $conflicts)"
fi

step "4. build and compile in the worktree"
(cd "$tree" && eval "$BUILD") || fail "the build failed after the merge; main is unchanged"
(cd "$tree" && eval "$COMPILE") || fail "the paper did not compile after the merge; main is unchanged"

step "5. commit what the build rewrote"
if [ -n "$(git -C "$tree" status --porcelain --untracked-files=no)" ]; then
  git -C "$tree" add -u
  git -C "$tree" commit -q -m "build after merging $branch"
  step "   $(git -C "$tree" diff --stat HEAD~1 | tail -1)"
else
  step "   nothing: the build wrote what was already committed"
fi

merged=$(git -C "$tree" rev-parse HEAD)
step "6. main -> $(git rev-parse --short "$merged"), pushed; $branch removed"
git merge -q --ff-only "$merged"
git push -q "$REMOTE" main
for pdf in "$tree"/paper/*.pdf; do
  [ -f "$pdf" ] && cp "$pdf" paper/
done
git push -q "$REMOTE" --delete "$branch" 2>/dev/null || true
retire "$branch"   # its branch is merged by the fast-forward above; the other two tests are retire's own

step "7. publishing to the Overleaf mirror"
pushed=$("$PYTHON" code/publish.py push)
step "   $pushed"
