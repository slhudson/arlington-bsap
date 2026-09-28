#!/usr/bin/env bash
# Which Claude sessions are live in the primary checkout right now.
#
#   bash .claude/sessions.sh register   record this session, print the others
#   bash .claude/sessions.sh others     print the live pids, one per line
#
# Two callers share this so they cannot disagree: the SessionStart hook in
# .claude/settings.json, which advises at the start of a session, and
# .githooks/pre-commit, which refuses a commit in a shared checkout.
#
# One file per session under .claude/tmp/sessions/, named for the pid. The
# earlier design kept a single .claude/tmp/session.lock holding one pid, which
# each new session overwrote - so it could say "somebody else is here" once, at
# the moment of starting, and could never answer "how many are here now". A
# commit happens long after that moment, so it needs the count, and a directory
# gives one. docs/repository.md has the history.
#
# A session is live if its process still answers and its file is younger than a
# shift. Both tests matter: a killed session leaves its file behind, and a pid
# is reused eventually.
set -euo pipefail
cd "$(dirname "$0")/.."

SESSIONS=.claude/tmp/sessions
STALE=43200   # 12 hours, the same shift length the old lock used

# Worktrees have their own .git file; only the primary checkout is shared, and
# it is the only place this question means anything.
if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ]; then
  exit 0
fi

mkdir -p "$SESSIONS"
now=$(date +%s)

# Prune first, so both callers see the same list.
for f in "$SESSIONS"/*; do
  [ -e "$f" ] || continue
  pid=$(basename "$f")
  written=$(cat "$f" 2>/dev/null || echo 0)
  if ! kill -0 "$pid" 2>/dev/null || [ $((now - written)) -ge "$STALE" ]; then
    rm -f "$f"
  fi
done

case "${1:-others}" in
  register)
    # $PPID is the Claude process that ran the SessionStart hook.
    echo "$now" > "$SESSIONS/$PPID"
    for f in "$SESSIONS"/*; do
      [ -e "$f" ] || continue
      [ "$(basename "$f")" = "$PPID" ] || basename "$f"
    done
    ;;
  others)
    # No pid to exclude: a hook run by git cannot tell which session it serves,
    # so the caller asks "how many are here", not "is anyone but me here".
    for f in "$SESSIONS"/*; do
      [ -e "$f" ] || continue
      basename "$f"
    done
    ;;
  *)
    echo "usage: sessions.sh [register|others]" >&2
    exit 2
    ;;
esac
