"""Run the named steps of a stage, in one Python process.

    .venv/bin/python code/stage.py build elections members_claims ...
    .venv/bin/python code/stage.py clean residents members ...
    .venv/bin/python code/stage.py analysis residents_by_age members_age

run.sh calls this once per stage, so the interpreter, pandas and matplotlib
start once and not once per step. Each step is run exactly as
`python code/<stage>/<name>.py` from inside that folder would run it: the
folder on the path and as the working directory, its own file as the running
program (which is where paths.save() reads the name of what a figure writes),
and `__main__` as its name. The steps run in the order given. A step that
fails stops the stage with its name above its own traceback.

Two things differ by stage. The build and clean steps print the stage's
report, so their output is not silenced; a figure's prints are not the
build's report, so analysis silences them and prints one timed line per
figure instead. And only the build stage remembers what each step read
(paths.begin_step), so that is called where a stage's paths.py has it.
"""
import contextlib
import importlib
import os
import runpy
import sys
import time
from pathlib import Path

STAGES = ("build", "clean", "analysis")
CODE = Path(__file__).resolve().parent


def main(stage, names):
    if stage not in STAGES:
        raise SystemExit(f"stage is one of {', '.join(STAGES)}, not {stage!r}")
    figures = stage == "analysis"
    folder = CODE / stage
    sys.path.insert(0, str(folder))
    os.chdir(folder)
    paths = importlib.import_module("paths")
    for name in names:
        if hasattr(paths, "begin_step"):
            paths.begin_step()
        script = folder / f"{name}.py"
        if not script.exists():
            raise SystemExit(f"no {stage} step code/{stage}/{name}.py")
        sys.argv = [str(script)]
        started = time.time()
        try:
            if figures:
                with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
                    runpy.run_path(str(script), run_name="__main__")
            else:
                runpy.run_path(str(script), run_name="__main__")
        except SystemExit as e:
            if e.code not in (None, 0):
                print(f"\n{stage} step {name} stopped the stage", file=sys.stderr, flush=True)
                raise
        except BaseException:
            print(f"\n{stage} step {name} failed:", file=sys.stderr, flush=True)
            raise
        if figures:
            import matplotlib.pyplot as plt
            plt.close("all")
            print(f"  {name:<36}{time.time() - started:4.1f}s", flush=True)
        sys.stdout.flush()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
