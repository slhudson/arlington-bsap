"""Where the fetch scripts put what they download.

One paths.py per stage, deliberately: this one knows data/raw/ and nothing
below it. A fetch script names its own file under RAW.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
