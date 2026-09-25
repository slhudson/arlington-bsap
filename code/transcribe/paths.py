"""Where the transcription scripts find the scans and put what they read.

This one knows data/raw/ and data/transcribed/ and nothing below them
(CLAUDE.md).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
TRANSCRIBED = ROOT / "data" / "transcribed"
