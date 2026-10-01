"""Where the fetch scripts put what they download, and where their keys are.

This one knows data/raw/ and nothing below it (CLAUDE.md). It also reads
.env, because an account is the other thing this stage needs and the only
stage that needs one.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
ENV = ROOT / ".env"


def api_key(name):
    """The value of `name` in .env at the repository root. Only this stage
    asks: run.sh never touches the network (CLAUDE.md), so a missing key
    stops a fetch and nothing else."""
    if not ENV.exists():
        raise SystemExit(f"no .env at the repository root; see the docstring of the "
                         f"script you ran for the {name} it wants")
    for line in ENV.read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{name} not found in .env; add it from your account with that service")
