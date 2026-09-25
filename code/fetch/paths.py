"""Where the fetch scripts put what they download.

This one knows data/raw/ and nothing below it (CLAUDE.md).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
