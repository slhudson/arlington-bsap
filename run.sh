#!/usr/bin/env bash
# Rebuild everything from raw/. This is the only entry point: no figure is ever
# produced by hand, and nothing in data/ or figures/ is edited after the fact.
#
#   bash run.sh            build, then every figure
#   bash run.sh pct log    build, then only figures whose names match
#
# Invoke through bash rather than ./run.sh - Overleaf does not preserve Unix
# file permissions, so a push from Overleaf strips the executable bit.
#
# `set -e` matters: if a stage fails the run stops, rather than leaving a
# half-updated figures/ that looks like it succeeded.
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv: python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl"; exit 1; }

# Stage 1: raw/ -> data/. Every subjective decision about what a number IS
# happens here. Always runs, so data/ can never be stale relative to raw/.
echo "build"
(cd build && ../"$PY" clean.py)

# Stage 2: data/ -> figures/. Presentation only; analysis cannot see raw/.
echo "analysis"
scripts=(analysis/make_*.py)
if [ $# -gt 0 ]; then
  scripts=()
  for pat in "$@"; do scripts+=(analysis/make_*"$pat"*.py); done
fi
for s in "${scripts[@]}"; do
  printf '  %-44s' "$(basename "$s")"
  (cd analysis && ../"$PY" "$(basename "$s")") >/dev/null
  echo "ok"
done
echo "-> figures/ ($(ls figures | wc -l | tr -d ' ') files)"

# Overleaf syncs the WHOLE repo and recommends staying under 100MB. We chose a
# single repo on that basis, so the choice needs a tripwire rather than a note
# someone has to remember. See docs/questions.md Q6.
# This check must never be able to fail the build, so it tolerates tracked
# files that are missing from disk (e.g. deleted but not yet committed) and
# falls back to 0 rather than aborting under `set -e`.
kb=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] && kb=$(( kb + $(stat -f%z "$f") / 1024 ))
done < <(git ls-files -z 2>/dev/null) || true

if [ "$kb" -ge 81920 ]; then
  echo
  echo "WARNING: tracked files total $((kb/1024))MB, approaching Overleaf's 100MB ceiling."
  echo "         Time to revisit the one-repo decision - see docs/questions.md Q6."
fi
