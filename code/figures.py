"""Draw the figures named on the command line, in one Python process.

    .venv/bin/python code/figures.py residents_by_age members_age

run.sh calls this once for the figures it selects, so the interpreter, pandas
and matplotlib start once and not once per figure. Each step is run exactly
as `python code/analysis/<name>.py` would run it: its folder on the path, its
own file as the running program (which is where paths.save() reads the name
of what it writes), and `__main__` as its name. A step that fails stops the
run with its own traceback; run.sh then checks that each step wrote its file.
"""
import contextlib
import os
import runpy
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS = Path(__file__).resolve().parent / "analysis"


def main(names):
    sys.path.insert(0, str(ANALYSIS))
    os.chdir(ANALYSIS)
    for name in names:
        script = ANALYSIS / f"{name}.py"
        if not script.exists():
            raise SystemExit(f"no figure step code/analysis/{name}.py")
        sys.argv = [str(script)]
        started = time.time()
        # A step's own prints are not the build's report.
        with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
            runpy.run_path(str(script), run_name="__main__")
        plt.close("all")
        print(f"  {name:<36}{time.time() - started:4.1f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
