#!/usr/bin/env bash
# Rebuild every figure from raw/. This is the only entry point: no figure is
# ever produced by hand, and nothing in figures/ is edited after the fact.
#
#   ./run.sh            rebuild all figures
#   ./run.sh pct log    rebuild only the scripts whose names match these words
#
# `set -e` matters here: if any figure fails, the run stops rather than
# leaving a half-updated figures/ that looks like it succeeded.
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv: run  python3 -m venv .venv && .venv/bin/pip install pandas matplotlib openpyxl"; exit 1; }

scripts=(build/make_*.py)
if [ $# -gt 0 ]; then
  scripts=()
  for pat in "$@"; do scripts+=(build/make_*"$pat"*.py); done
fi

for s in "${scripts[@]}"; do
  printf '%-46s' "$(basename "$s")"
  "$PY" "$s" >/dev/null
  echo "ok"
done
echo "-> figures/ ($(ls figures | wc -l | tr -d ' ') files)"

# Overleaf syncs the WHOLE repo and recommends staying under 100MB. We chose a
# single repo on that basis, so the choice needs a tripwire rather than a note
# someone has to remember: warn at 80MB, which is when splitting paper/ into
# its own repo should be reconsidered. See questions.md Q6.
# Measure what Overleaf actually receives: the git-tracked files. du on the
# working directory would count .venv and figures/ too, which never sync.
kb=$(git ls-files -z | xargs -0 stat -f%z 2>/dev/null | awk '{s+=$1} END {print int(s/1024)}')
if [ "${kb:-0}" -ge 81920 ]; then
  echo
  echo "WARNING: tracked files total $((kb/1024))MB, approaching Overleaf's 100MB ceiling."
  echo "         Time to revisit the one-repo decision - see questions.md Q6."
fi
