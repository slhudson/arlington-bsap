#!/usr/bin/env bash
# Which Claude sessions are live in the primary checkout right now.
#
#   bash .claude/sessions.sh others     print the live session ids, one per line
#   bash .claude/sessions.sh register   the same, less the caller's own
#
# Two callers share this so they cannot disagree: the SessionStart hook in
# .claude/settings.json, which advises at the start of a session, and
# .githooks/pre-commit, which refuses a commit in a shared checkout.
#
# A session is live if Claude Code has written to its transcript recently.
# Nothing registers and nothing is pruned: Claude writes the transcripts
# itself, one per session under ~/.claude/projects/<cwd with slashes turned
# to dashes>/, and a running session appends to its own as it works. Reading
# those asks what is true rather than trusting sessions to say so.
#
# The design this replaced had each session write a file named for $PPID and
# tested liveness with kill -0. In a hook $PPID is the shell that invoked the
# script, which exits immediately, so every registration was pruned by the
# next read and the directory stood empty. Both callers then believed nobody
# was here: every SessionStart said "this is the only live session", and the
# pre-commit hook never refused a commit. Found on 1 October 2026 with three
# sessions live in this checkout. docs/repository.md has the incident the
# guard exists for, and this one.
#
# Failure here is loud, because silence is how the old design went wrong: if
# the transcripts cannot be found this says so and exits non-zero rather than
# reporting an empty checkout.
set -euo pipefail
cd "$(dirname "$0")/.."

# A session idle longer than this is treated as gone. A session that is
# committing is always fresh, so the window only governs how long an idle one
# goes on blocking it: long enough to cover a lunch, short enough that
# yesterday's sessions do not count.
HEARTBEAT=${SESSIONS_HEARTBEAT:-14400}   # 4 hours

# Worktrees have their own .git file; only the primary checkout is shared, and
# it is the only place this question means anything.
if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ]; then
  exit 0
fi


live() {
  # Claude Code names a project's directory for its path, slashes turned to
  # dashes. SESSIONS_DIR overrides it so code/tests.py can hand this a
  # directory it built itself.
  local dir=${SESSIONS_DIR:-"$HOME/.claude/projects/$(pwd -P | tr / -)"}
  if [ ! -d "$dir" ]; then
    echo "sessions.sh: no transcripts under $dir, so how many sessions are live" \
         "here cannot be answered" >&2
    exit 1
  fi
  local now written f
  now=$(date +%s)
  for f in "$dir"/*.jsonl; do
    [ -e "$f" ] || continue
    # -f %m is stat's mtime on macOS, which is what this repo runs on.
    written=$(stat -f %m "$f" 2>/dev/null || echo 0)
    [ $((now - written)) -lt "$HEARTBEAT" ] && basename "$f" .jsonl
  done
  return 0
}


case "${1:-others}" in
  others)
    # No session to leave out: a hook run by git cannot tell which session it
    # serves, so the caller asks "how many are here", not "is anyone but me".
    live
    ;;
  register)
    # The SessionStart hook is given its own session on stdin as JSON, and
    # wants the others. Without it - run by hand at a terminal - nothing is
    # left out.
    self=
    [ -t 0 ] || self=$(cat | sed -n \
        's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
    if [ -n "$self" ]; then
      live | grep -vxF "$self" || true
    else
      live
    fi
    ;;
  *)
    echo "usage: sessions.sh [others|register]" >&2
    exit 2
    ;;
esac
