#!/usr/bin/env bash
# Merge a thread's branch into main, the way it was done by hand six times on
# 5 October 2026, with the places to slip taken out of a person's hands.
#
#   bash code/merge.sh <branch>
#
# One line per step. The steps, in order, and what each one refuses:
#
#   1. A scratch worktree on origin/main, after a fetch, so the merge is made
#      against what is pushed and not against a stale local main.
#   2. The branch merged. A conflict stops it: docs/questions.csv,
#      paper/punchlist.md and the negatives file merge by union
#      (.gitattributes), so anything still conflicting is two sessions
#      editing one line, which is a person's decision. The worktree is
#      removed and nothing has changed.
#   3. bash run.sh, then code/paper.py and code/paper.py timelines, in the
#      worktree. A failure stops it before anything reaches main: a commit
#      chained after a failing build was the first of the slips.
#   4. What the build rewrote (figures/, data/clean/, the .tex files the
#      analysis stage writes) committed in the worktree, so a figure rebuilt
#      there is not lost when the worktree goes - the third slip.
#   5. main fast-forwarded to the merge and pushed; the compiled PDF copied
#      to the primary checkout; the worktree and the branch removed, locally
#      and on origin.
#
# The build and the compile are the commands BUILD and COMPILE below;
# code/tests.py substitutes them to prove the script stops when either fails
# and goes on when both pass. Nothing else overrides them.
set -euo pipefail

usage() { echo "usage: bash code/merge.sh <branch>" >&2; exit 2; }
[ $# -eq 1 ] || usage
branch=$1

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
BUILD=${BUILD:-"bash run.sh"}
COMPILE=${COMPILE:-".venv/bin/python code/paper.py && .venv/bin/python code/paper.py timelines"}
REMOTE=${REMOTE:-origin}

step() { printf '%s\n' "$*"; }
fail() { printf 'stopped: %s\n' "$*" >&2; exit 1; }

# The primary checkout must be on main and have nothing staged or modified in
# the files the merge will move, or the fast-forward at the end cannot land.
# Checking "clean" is the simplest form of that and the one a reader expects.
[ "$(git rev-parse --git-dir)" = ".git" ] || fail "run this from the primary checkout, not a worktree"
[ "$(git branch --show-current)" = "main" ] || fail "the primary checkout is on $(git branch --show-current), not main"
[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "the primary checkout has uncommitted changes; commit or stash them first"

git fetch -q "$REMOTE" main
git rev-parse -q --verify "$branch" >/dev/null 2>&1 || git fetch -q "$REMOTE" "$branch:$branch" 2>/dev/null \
  || fail "no branch $branch here or on $REMOTE"
[ "$(git merge-base --is-ancestor "$REMOTE/main" main && echo yes)" = yes ] \
  || fail "local main is behind $REMOTE/main; pull first"
[ "$(git rev-parse main)" = "$(git rev-parse "$REMOTE/main")" ] \
  || fail "local main has commits $REMOTE/main does not; push them first"

name=merge-$(echo "$branch" | tr '/' '-')
tree=.claude/worktrees/$name
cleanup() {
  git worktree remove --force "$tree" >/dev/null 2>&1 || true
  git branch -D -q "$name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

step "1. worktree $tree on $REMOTE/main ($(git rev-parse --short "$REMOTE/main"))"
mkdir -p .claude/worktrees
git worktree add -q "$tree" -b "$name" "$REMOTE/main"
# The build wants the venv and run.sh wants it beside the script; a worktree
# has neither, and .venv is gitignored, so the primary's serves.
[ -e "$tree/.venv" ] || ln -s "$ROOT/.venv" "$tree/.venv"

step "2. merge $branch ($(git rev-parse --short "$branch"))"
if ! git -C "$tree" merge -q -m "merge $branch" "$branch" >/dev/null 2>&1; then
  conflicts=$(git -C "$tree" diff --name-only --diff-filter=U)
  git -C "$tree" merge --abort 2>/dev/null || true
  fail "conflicts a person has to resolve, outside the union-merged files:
$(printf '  %s\n' $conflicts)"
fi

step "3. build and compile in the worktree"
(cd "$tree" && eval "$BUILD") || fail "the build failed after the merge; main is unchanged"
(cd "$tree" && eval "$COMPILE") || fail "the paper did not compile after the merge; main is unchanged"

step "4. commit what the build rewrote"
if [ -n "$(git -C "$tree" status --porcelain --untracked-files=no)" ]; then
  git -C "$tree" add -u
  git -C "$tree" commit -q -m "build after merging $branch"
  step "   $(git -C "$tree" diff --stat HEAD~1 | tail -1)"
else
  step "   nothing: the build wrote what was already committed"
fi

merged=$(git -C "$tree" rev-parse HEAD)
step "5. main -> $(git rev-parse --short "$merged"), pushed; $branch removed"
git merge -q --ff-only "$merged"
git push -q "$REMOTE" main
for pdf in arlington-bsap timelines; do
  [ -f "$tree/paper/$pdf.pdf" ] && cp "$tree/paper/$pdf.pdf" "paper/$pdf.pdf"
done
git worktree remove --force "$tree"
git branch -D -q "$name"
git branch -D -q "$branch" 2>/dev/null || true
git push -q "$REMOTE" --delete "$branch" 2>/dev/null || true
trap - EXIT
