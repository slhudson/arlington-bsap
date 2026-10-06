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
#   3. The build and the compiles, decided from what the branch touched
#      (git diff --name-only against origin/main), not run unconditionally:
#        - bash run.sh only if a path under code/, data/, style/ or run.sh
#          itself changed; otherwise just code/tests.py, which still guards
#          the tracker, the bibliography and the Drive filing and stays
#          cheap on a checkout a fresh worktree has not built.
#        - code/paper.py (arlington-bsap.pdf) only if a path under paper/ or
#          figures/ changed, or the build ran.
#        - code/paper.py timelines (timelines.pdf) only if
#          paper/timelines.tex or paper/sources.bib changed, or a figure it
#          inputs did.
#      A failure at any of the three stops it before anything reaches main:
#      a commit chained after a failing build was the first of the slips.
#   4. What the build rewrote (figures/, data/clean/, the .tex files the
#      analysis stage writes) committed in the worktree, so a figure rebuilt
#      there is not lost when the worktree goes - the third slip.
#   5. main fast-forwarded to the merge and pushed; the compiled PDF copied
#      to the primary checkout; the worktree and the branch removed, locally
#      and on origin.
#
# The build, the tests-only fallback and the two compiles are the commands
# BUILD, TESTS, COMPILE_PAPER and COMPILE_TIMELINES below; code/tests.py
# substitutes them to prove the script stops when one fails, skips the ones
# the diff rules out, and goes on when what runs passes. COMPILE, if set,
# overrides both compiles at once, for a test that does not care which one
# ran. Nothing else overrides them.
set -euo pipefail

usage() { echo "usage: bash code/merge.sh <branch>" >&2; exit 2; }
[ $# -eq 1 ] || usage
branch=$1

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
BUILD=${BUILD:-"bash run.sh"}
TESTS=${TESTS:-".venv/bin/python code/tests.py"}
COMPILE_PAPER=${COMPILE_PAPER:-${COMPILE:-".venv/bin/python code/paper.py"}}
COMPILE_TIMELINES=${COMPILE_TIMELINES:-${COMPILE:-".venv/bin/python code/paper.py timelines"}}
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
changed=$(git -C "$tree" diff --name-only "$REMOTE/main...HEAD")

build_needed=no
if printf '%s\n' "$changed" | grep -qE '^(code/|data/|style/)|^run\.sh$'; then
  build_needed=yes
fi

if [ "$build_needed" = yes ]; then
  (cd "$tree" && eval "$BUILD") || fail "the build failed after the merge; main is unchanged"
else
  step "   figures: skipped, the branch changed nothing under code/, data/ or style/"
  (cd "$tree" && eval "$TESTS") || fail "the tests failed after the merge; main is unchanged"
fi

paper_needed=$build_needed
if [ "$paper_needed" = no ] && printf '%s\n' "$changed" | grep -qE '^(paper/|figures/)'; then
  paper_needed=yes
fi
if [ "$paper_needed" = yes ]; then
  (cd "$tree" && eval "$COMPILE_PAPER") || fail "the paper did not compile after the merge; main is unchanged"
else
  step "   arlington-bsap.pdf: skipped, the branch changed nothing under paper/ or figures/, and the build did not run"
fi

# timelines.pdf also recompiles when a figure it inputs changed, read from
# the merged tree so a branch that adds a new \includegraphics is caught.
timelines_figs=$(grep -oE 'figures/(pdf|png)/[A-Za-z0-9_]+\.(pdf|png)' "$tree/paper/timelines.tex" 2>/dev/null | sort -u || true)
timelines_needed=no
if printf '%s\n' "$changed" | grep -qxE 'paper/timelines\.tex|paper/sources\.bib'; then
  timelines_needed=yes
elif [ -n "$timelines_figs" ]; then
  while IFS= read -r f; do
    if [ -n "$f" ] && printf '%s\n' "$changed" | grep -qxF "$f"; then
      timelines_needed=yes
    fi
  done <<< "$timelines_figs"
fi
if [ "$timelines_needed" = yes ]; then
  (cd "$tree" && eval "$COMPILE_TIMELINES") || fail "timelines.pdf did not compile after the merge; main is unchanged"
else
  step "   timelines.pdf: skipped, the branch changed neither paper/timelines.tex, paper/sources.bib, nor a figure it inputs"
fi

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
