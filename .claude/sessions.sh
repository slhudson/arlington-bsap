#!/usr/bin/env bash
# Which other Claude sessions are live in the primary checkout right now.
#
#   bash .claude/sessions.sh others     print their pids, one per line
#   bash .claude/sessions.sh register   the same; the SessionStart hook's name
#
# Two callers share this so they cannot disagree: the SessionStart hook in
# .claude/settings.json, which advises at the start of a session, and
# .githooks/pre-commit, which refuses a commit in a shared checkout. Both run
# as descendants of the session that asks, so both can be told about the
# others and leave the asker out.
#
# Claude Code opens one socket per live session at /tmp/cc-socks/<pid>.sock.
# That is the signal used here: the pid is testable with kill -0, and lsof
# gives the process's working directory, so a session counts only if it is
# working in this checkout. The asking session is found by walking up from
# this script until a parent turns out to own one of those sockets.
#
# Two earlier designs failed in opposite directions, and both are why the
# tests below exist.
#
# Sessions used to register themselves, writing a file named $PPID. In a hook
# $PPID is the invoking shell, which exits at once, so the next read found a
# dead process and pruned the file. The directory was always empty, every
# SessionStart said "this is the only live session", and .githooks/pre-commit
# never refused a commit.
#
# Replacing that, liveness was read from the per-session transcripts under
# ~/.claude/projects/, counting any written to within four hours. That
# over-counted: a transcript keeps its timestamp after its session exits, and
# subagents write transcripts of their own. Six were counted in a checkout
# holding four sessions, which refuses every commit and teaches everyone
# --no-verify - worse than the silence it replaced. A socket is held open by
# a process or it is not, so there is no window to tune.
#
# Failure is loud. An empty answer and no answer must not look alike: that is
# how the first design hid.
set -euo pipefail
cd "$(dirname "$0")/.."

SOCKS=${CC_SOCKS:-/tmp/cc-socks}

# Worktrees have their own .git file; only the primary checkout is shared, and
# it is the only place this question means anything.
if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ]; then
  exit 0
fi

if [ ! -d "$SOCKS" ]; then
  echo "sessions.sh: no session sockets under $SOCKS, so how many sessions are" \
       "live here cannot be answered" >&2
  exit 1
fi

here=$(pwd -P)

# The pid of a live session working in this checkout, or nothing.
session_at_here() {
  local pid=$1
  kill -0 "$pid" 2>/dev/null || return 0
  local cwd
  cwd=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1)
  [ "$cwd" = "$here" ] && echo "$pid"
  return 0
}

# Which of those sessions this script is running under. A hook is a child of
# the session that triggered it, so its own session is somewhere above it.
asker() {
  local p=$$ i
  for i in 1 2 3 4 5 6 7 8; do
    [ -S "$SOCKS/$p.sock" ] && { echo "$p"; return 0; }
    p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
    { [ -z "$p" ] || [ "$p" -le 1 ]; } && return 0
  done
  return 0
}

case "${1:-others}" in
  others|register)
    self=$(asker)
    for s in "$SOCKS"/*.sock; do
      [ -S "$s" ] || continue
      pid=$(basename "$s" .sock)
      [ "$pid" = "$self" ] && continue
      session_at_here "$pid"
    done
    ;;
  *)
    echo "usage: sessions.sh [others|register]" >&2
    exit 2
    ;;
esac
