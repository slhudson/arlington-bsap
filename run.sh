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
