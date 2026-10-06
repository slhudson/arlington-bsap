"""Run the named steps of the build or clean stage, in one Python process.

    .venv/bin/python code/stage.py build elections members_claims ...
    .venv/bin/python code/stage.py clean residents members ...

run.sh calls this once per stage, so the interpreter and pandas start once
and not once per step; code/figures.py does the same for the figures. Each
step is run exactly as `python code/<stage>/<name>.py` from inside that
folder would run it: the folder on the path and as the working directory, its
own file as the running program, `__main__` as its name. The steps run in the
order given, and what they print is the stage's report, so it is not
silenced. A step that fails stops the stage with its name above its own
traceback.
"""
import importlib
import os
import runpy
import sys
from pathlib import Path

STAGES = ("build", "clean")
CODE = Path(__file__).resolve().parent


def main(stage, names):
    if stage not in STAGES:
        raise SystemExit(f"stage is one of {', '.join(STAGES)}, not {stage!r}")
    folder = CODE / stage
    sys.path.insert(0, str(folder))
    os.chdir(folder)
    paths = importlib.import_module("paths")
    for name in names:
        if hasattr(paths, "begin_step"):      # only the build stage remembers what a step read
            paths.begin_step()
        script = folder / f"{name}.py"
        if not script.exists():
            raise SystemExit(f"no {stage} step code/{stage}/{name}.py")
        sys.argv = [str(script)]
        try:
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit as e:
            if e.code not in (None, 0):
                print(f"\n{stage} step {name} stopped the stage", file=sys.stderr, flush=True)
                raise
        except BaseException:
            print(f"\n{stage} step {name} failed:", file=sys.stderr, flush=True)
            raise
        sys.stdout.flush()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
