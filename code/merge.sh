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
#      The worktree is removed and nothing has changed. One conflict is
#      settled here: a build output (under figures/ or data/clean/) that one
#      side deleted and the other rebuilt takes the branch's side, since the
#      build recreates whatever the code still produces. And a line the
#      branch deleted from docs/punchlist.md, which the union merge brings
#      back when main appended beside it, is removed again and named
#      (code/merge_punchlist.py).
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
#
# A lock, held for the whole run and shared by every worktree and checkout of
# the clone, keeps two merges from running at once: the scratch worktree in
# step 2 is named for the branch, and two merges going at the same time could
# each remove the other's mid-build. A merge that finds the lock held by a
# live process stops at once, naming the branch and since when; one whose
# process has died is taken over, since a crashed run must never block merges
# forever.
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

GITCOMMON=$(git rev-parse --path-format=absolute --git-common-dir)
LOCK="$GITCOMMON/merge.lock"
take_lock() {
  mkdir "$LOCK" 2>/dev/null || return 1
  { echo "holder_pid=$$"; echo "holder_branch=$branch"; echo "holder_since=$(date)"; } > "$LOCK/info"
}
if ! take_lock; then
  holder_pid= holder_branch= holder_since=
  [ -f "$LOCK/info" ] && . "$LOCK/info"
  if [ -n "$holder_pid" ] && kill -0 "$holder_pid" 2>/dev/null; then
    fail "$holder_branch has been merging since $holder_since (pid $holder_pid); wait for it to finish"
  fi
  step "   the lock was held by pid ${holder_pid:-?} (dead); taking it over"
  rm -rf "$LOCK"
  take_lock || fail "could not take the merge lock at $LOCK"
fi
trap 'rm -rf "$LOCK"' EXIT

step "1. checking the Overleaf mirror for an edit to pull back"
pulled=$("$PYTHON" code/publish.py pull)
step "   $pulled"
case "$pulled" in
  "pull: branch "*)
    # Matches both the fresh "pull: branch X, ready for ..." and the
    # idempotent "pull: branch X already holds the mirror's edit, merge it"
    # (publish.py pull, called again after an earlier pull already made this
    # branch). Either way, when X is the branch this run was asked to merge,
    # the edit is already sitting on it and merging continues below; only a
    # different branch stops this run.
    waiting=$(printf '%s' "$pulled" | sed -n 's/^pull: branch \([^, ]*\).*/\1/p')
    [ "$waiting" = "$branch" ] || fail "an edit from Overleaf is waiting on $waiting; merge it first:
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
# The scratch worktree is this script's own, so it goes whatever happened,
# and so does the lock taken above.
cleanup() {
  git worktree remove --force "$tree" >/dev/null 2>&1 || true
  git branch -D -q "$name" >/dev/null 2>&1 || true
  rm -rf "$LOCK"
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
# A worktree or branch already named this is a leftover from a run that
# crashed before cleaning up; the lock just taken proves nothing live still
# holds it, so it is safe to clear rather than fail on "already exists".
git worktree remove --force "$tree" >/dev/null 2>&1 || true
git branch -D -q "$name" >/dev/null 2>&1 || true
git worktree add -q "$tree" -b "$name" "$REMOTE/main"

base=$(git merge-base "$REMOTE/main" "$branch")
step "3. merge $branch ($(git rev-parse --short "$branch"))"
if ! git -C "$tree" merge -q -m "merge $branch" "$branch" >/dev/null 2>&1; then
  # A file one side deleted and the other changed (modify/delete) is not a
  # disagreement when it is a build output: the build rewrites figures/ and
  # data/clean/ from the code, so the branch's side is taken - a deletion
  # stays deleted, because anything the code still produces comes back in
  # step 4 - and the merge goes on. Anywhere else it is a person's decision,
  # and the two commands that settle it each way are printed.
  manual="" other=""
  while IFS= read -r line; do
    code=${line:0:2}; path=${line:3}
    case "$code:$path" in
      UD:figures/*|UD:data/clean/*) git -C "$tree" rm -q -- "$path"
                                    step "   $path: deleted on $branch, rebuilt on main; the deletion is kept" ;;
      DU:figures/*|DU:data/clean/*) git -C "$tree" add -- "$path"
                                    step "   $path: deleted on main, changed on $branch; the branch's file is kept" ;;
      UD:*) manual="$manual
  $path  (deleted on $branch, changed on main)
    keep the deletion:  git rm -- $path
    keep main's file:   git checkout --ours -- $path && git add -- $path" ;;
      DU:*) manual="$manual
  $path  (deleted on main, changed on $branch)
    keep the deletion:  git rm -- $path
    keep the branch's:  git checkout --theirs -- $path && git add -- $path" ;;
      *) other="$other
  $path" ;;
    esac
  done < <(git -C "$tree" status --porcelain --untracked-files=no | grep -E '^(DD|AU|UD|UA|DU|AA|UU) ')
  if [ -n "$manual$other" ]; then
    git -C "$tree" merge --abort 2>/dev/null || true
    [ -z "$other" ] || msg="conflicts a person has to resolve, outside the union-merged files:$other"
    [ -z "$manual" ] || msg="${msg:+$msg
}a file one side deleted and the other changed; merge $branch in a worktree of your own, then:$manual"
    fail "$msg"
  fi
  git -C "$tree" commit -q --no-edit
fi

# A union merge keeps both sides of a disputed hunk, so a line the branch
# deleted from the punch list returns when main appended beside it.
"$PYTHON" code/merge_punchlist.py "$tree" "$base" "$branch"
if [ -n "$(git -C "$tree" status --porcelain --untracked-files=no -- docs/punchlist.md)" ]; then
  git -C "$tree" commit -q -m "punch list: lines $branch deleted stay deleted" -- docs/punchlist.md
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
