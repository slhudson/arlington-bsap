"""Where the transcription scripts find the scans and put what they read.

This one knows sources/ and data/transcribed/ and nothing below them
(CLAUDE.md).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources"
# The publishers' folders this stage reads, by the short names it uses.
CENSUS_BUREAU = SOURCES / "government" / "federal" / "us_census_bureau"
ARLINGTON_COUNTY = SOURCES / "government" / "local" / "arlington_county"
MAGAZINE = SOURCES / "press" / "arlington_historical_magazine"
TRANSCRIBED = ROOT / "data" / "transcribed"
BY_CLAUDE = TRANSCRIBED / "by_claude"
